import asyncio
from typing import Optional, Callable
from logger_config import logger
from utils.delay_manager import delay_manager
from utils.rate_limiter import rate_limiter
from config import config

class CommandHandler:
    """Handles bot commands"""
    
    def __init__(self):
        self.commands = {}
        self.aliases = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register default commands"""
        # Will be populated by command decorators
        pass
    
    def register_command(self, name: str, handler: Callable, aliases: list = None):
        """Register a command"""
        self.commands[name] = handler
        if aliases:
            for alias in aliases:
                self.aliases[alias] = name
        logger.debug(f"Command registered: {name}")
    
    async def execute(self, command: str, *args, **kwargs) -> dict:
        """Execute a command"""
        try:
            # Resolve alias
            actual_command = self.aliases.get(command, command)
            
            if actual_command not in self.commands:
                return {
                    'success': False,
                    'message': f'Command not found: {command}',
                    'data': None
                }
            
            # Check rate limit
            if config.RATE_LIMIT_ENABLED:
                await rate_limiter.wait_if_needed(f"cmd_{actual_command}")
            
            # Execute command
            handler = self.commands[actual_command]
            result = await handler(*args, **kwargs) if asyncio.iscoroutinefunction(handler) else handler(*args, **kwargs)
            
            return {
                'success': True,
                'message': 'Command executed successfully',
                'data': result
            }
        
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                'success': False,
                'message': str(e),
                'data': None
            }


class FFCommandHandler(CommandHandler):
    """Free Fire command handler"""
    
    def __init__(self, ff_bot):
        super().__init__()
        self.ff_bot = ff_bot
        self._register_ff_commands()
    
    def _register_ff_commands(self):
        """Register Free Fire specific commands"""
        self.register_command('emote', self.cmd_emote, ['e'])
        self.register_command('spam', self.cmd_spam, ['s'])
        self.register_command('message', self.cmd_message, ['msg', 'm'])
        self.register_command('status', self.cmd_status, ['st'])
        self.register_command('info', self.cmd_info, ['i'])
        self.register_command('help', self.cmd_help, ['h'])
    
    async def cmd_emote(self, target_uid: str, emote_id: int, times: int = 1) -> dict:
        """Emote command"""
        try:
            if times > 5:
                times = 5  # Limit spam
            
            success_count = 0
            for i in range(times):
                if await self.ff_bot.send_emote(target_uid, emote_id):
                    success_count += 1
                await delay_manager.emote_delay()
            
            return {
                'emote_id': emote_id,
                'target_uid': target_uid,
                'success': success_count,
                'total': times
            }
        except Exception as e:
            logger.error(f"Emote command error: {e}")
            raise
    
    async def cmd_spam(self, chat_id: str, message: str, times: int = 1) -> dict:
        """Spam command"""
        try:
            if times > 10:
                times = 10  # Limit spam
            
            success_count = 0
            for i in range(times):
                if await self.ff_bot.send_message(chat_id, message):
                    success_count += 1
                await delay_manager.message_delay()
            
            return {
                'chat_id': chat_id,
                'message': message[:50],
                'success': success_count,
                'total': times
            }
        except Exception as e:
            logger.error(f"Spam command error: {e}")
            raise
    
    async def cmd_message(self, chat_id: str, message: str) -> dict:
        """Send message command"""
        success = await self.ff_bot.send_message(chat_id, message)
        return {
            'chat_id': chat_id,
            'message': message,
            'success': success
        }
    
    async def cmd_status(self) -> dict:
        """Get bot status"""
        return {
            'connected': self.ff_bot.tcp_conn.connected if self.ff_bot.tcp_conn else False,
            'uid': self.ff_bot.ff_uid,
            'running': self.ff_bot.running
        }
    
    async def cmd_info(self, target_uid: str) -> dict:
        """Get player info"""
        # This would call the actual Free Fire API
        return {
            'uid': target_uid,
            'status': 'unknown'  # Would be filled from actual API
        }
    
    async def cmd_help(self) -> dict:
        """Show help"""
        return {
            'commands': list(self.commands.keys()),
            'aliases': self.aliases
        }
