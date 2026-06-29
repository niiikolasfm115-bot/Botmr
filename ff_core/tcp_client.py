import asyncio
import struct
from typing import Optional, Tuple
from logger_config import logger
from utils.encryption import encryption_manager
from utils.delay_manager import delay_manager
from utils.rate_limiter import rate_limiter
from config import config

class TCPConnection:
    """Manages TCP connection to Free Fire server"""
    
    def __init__(self, host: str, port: int, key: bytes = None, iv: bytes = None):
        self.host = host
        self.port = port
        self.key = key
        self.iv = iv
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
    
    async def connect(self) -> bool:
        """Connect to Free Fire server"""
        try:
            logger.info(f"Attempting to connect to {self.host}:{self.port}")
            
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=config.CONNECTION_TIMEOUT
            )
            
            self.connected = True
            self.reconnect_attempts = 0
            logger.info(f"✅ Connected to {self.host}:{self.port}")
            return True
            
        except asyncio.TimeoutError:
            logger.error(f"❌ Connection timeout to {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
        
        self.connected = False
        return False
    
    async def reconnect(self) -> bool:
        """Reconnect to server with exponential backoff"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            return False
        
        self.reconnect_attempts += 1
        delay = config.RECONNECT_DELAY * (2 ** (self.reconnect_attempts - 1))
        
        logger.warning(f"Reconnecting in {delay}s (attempt {self.reconnect_attempts})")
        await asyncio.sleep(delay)
        
        return await self.connect()
    
    async def send_packet(self, data: bytes) -> bool:
        """Send encrypted packet to server"""
        if not self.connected or not self.writer:
            logger.error("Not connected to server")
            return False
        
        try:
            # Encrypt data if key and IV available
            if self.key and self.iv:
                encrypted_data = encryption_manager.encrypt_aes(data, self.key, self.iv)
            else:
                encrypted_data = data
            
            # Add packet header (length)
            packet = struct.pack('>H', len(encrypted_data)) + encrypted_data
            
            self.writer.write(packet)
            await asyncio.wait_for(self.writer.drain(), timeout=config.REQUEST_TIMEOUT)
            
            return True
            
        except asyncio.TimeoutError:
            logger.error("Send timeout")
            self.connected = False
        except Exception as e:
            logger.error(f"Send error: {e}")
            self.connected = False
        
        return False
    
    async def receive_packet(self, timeout: float = 10.0) -> Optional[bytes]:
        """Receive encrypted packet from server"""
        if not self.connected or not self.reader:
            return None
        
        try:
            # Read packet header (length)
            header = await asyncio.wait_for(
                self.reader.readexactly(2),
                timeout=timeout
            )
            packet_length = struct.unpack('>H', header)[0]
            
            # Read packet data
            encrypted_data = await asyncio.wait_for(
                self.reader.readexactly(packet_length),
                timeout=timeout
            )
            
            # Decrypt data if key and IV available
            if self.key and self.iv:
                decrypted_data = encryption_manager.decrypt_aes(encrypted_data, self.key, self.iv)
            else:
                decrypted_data = encrypted_data
            
            return decrypted_data
            
        except asyncio.TimeoutError:
            logger.debug("Receive timeout")
        except Exception as e:
            logger.error(f"Receive error: {e}")
            self.connected = False
        
        return None
    
    async def close(self):
        """Close connection"""
        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        
        self.connected = False
        logger.info("Connection closed")


class FFProtocol:
    """Free Fire protocol handler"""
    
    # Common packet types
    PACKET_LOGIN = 1
    PACKET_HEARTBEAT = 2
    PACKET_MESSAGE = 3
    PACKET_EMOTE = 4
    PACKET_SQUAD = 5
    PACKET_MATCH = 6
    PACKET_STATUS = 7
    
    @staticmethod
    def create_heartbeat_packet() -> bytes:
        """Create heartbeat packet"""
        return bytes([0x00, 0x00, 0x00, 0x02, 0x00, 0x00])
    
    @staticmethod
    def create_message_packet(chat_id: str, message: str, msg_type: int = 0) -> bytes:
        """Create message packet"""
        try:
            msg_bytes = message.encode('utf-8')
            packet = bytearray()
            packet.append(0x03)  # Message type
            packet.extend(chat_id.encode('utf-8')[:20])
            packet.extend(struct.pack('>H', len(msg_bytes)))
            packet.extend(msg_bytes)
            return bytes(packet)
        except Exception as e:
            logger.error(f"Error creating message packet: {e}")
            return b''
    
    @staticmethod
    def create_emote_packet(target_uid: str, emote_id: int) -> bytes:
        """Create emote packet"""
        try:
            packet = bytearray()
            packet.append(0x04)  # Emote type
            uid_bytes = target_uid.encode('utf-8')
            packet.extend(struct.pack('>H', len(uid_bytes)))
            packet.extend(uid_bytes)
            packet.extend(struct.pack('>I', emote_id))
            return bytes(packet)
        except Exception as e:
            logger.error(f"Error creating emote packet: {e}")
            return b''
    
    @staticmethod
    def create_squad_packet(action: str, target_uid: str = None) -> bytes:
        """Create squad packet"""
        try:
            packet = bytearray()
            packet.append(0x05)  # Squad type
            packet.append(ord(action[0]))  # Action
            if target_uid:
                uid_bytes = target_uid.encode('utf-8')
                packet.extend(struct.pack('>H', len(uid_bytes)))
                packet.extend(uid_bytes)
            return bytes(packet)
        except Exception as e:
            logger.error(f"Error creating squad packet: {e}")
            return b''


class FFBot:
    """Main Free Fire Bot class"""
    
    def __init__(self, ff_uid: str, access_token: str, key: bytes = None, iv: bytes = None):
        self.ff_uid = ff_uid
        self.access_token = access_token
        self.key = key or encryption_manager.key
        self.iv = iv or encryption_manager.iv
        self.tcp_conn = None
        self.running = False
    
    async def connect(self, host: str = config.FF_SERVER_IP, port: int = config.FF_SERVER_PORT) -> bool:
        """Connect to Free Fire"""
        self.tcp_conn = TCPConnection(host, port, self.key, self.iv)
        return await self.tcp_conn.connect()
    
    async def disconnect(self):
        """Disconnect from Free Fire"""
        if self.tcp_conn:
            await self.tcp_conn.close()
        self.running = False
    
    async def send_message(self, chat_id: str, message: str) -> bool:
        """Send message with rate limiting"""
        # Check rate limit
        if config.RATE_LIMIT_ENABLED:
            await rate_limiter.wait_if_needed(f"message_{chat_id}")
        
        # Apply delay
        await delay_manager.message_delay()
        
        packet = FFProtocol.create_message_packet(chat_id, message)
        if not packet:
            return False
        
        success = await self.tcp_conn.send_packet(packet)
        if success:
            logger.info(f"✅ Message sent to {chat_id}: {message[:50]}")
        else:
            logger.error(f"❌ Failed to send message to {chat_id}")
        
        return success
    
    async def send_emote(self, target_uid: str, emote_id: int) -> bool:
        """Send emote with rate limiting"""
        # Check rate limit
        if config.RATE_LIMIT_ENABLED:
            await rate_limiter.wait_if_needed(f"emote_{target_uid}")
        
        # Apply delay
        await delay_manager.emote_delay()
        
        packet = FFProtocol.create_emote_packet(target_uid, emote_id)
        if not packet:
            return False
        
        success = await self.tcp_conn.send_packet(packet)
        if success:
            logger.info(f"✅ Emote {emote_id} sent to {target_uid}")
        else:
            logger.error(f"❌ Failed to send emote to {target_uid}")
        
        return success
    
    async def send_emote_spam(self, target_uids: list, emote_id: int, times: int = 1) -> int:
        """Send emote spam with protection against ban"""
        success_count = 0
        
        for uid in target_uids:
            for i in range(times):
                if await self.send_emote(uid, emote_id):
                    success_count += 1
                await delay_manager.emote_delay()
            
            # Longer delay between different users
            await delay_manager.random_delay(1.0, 2.0)
        
        logger.info(f"✅ Emote spam completed: {success_count}/{len(target_uids) * times} sent")
        return success_count
    
    async def send_message_spam(self, chat_id: str, message: str, times: int = 1) -> int:
        """Send message spam with protection"""
        success_count = 0
        
        for i in range(times):
            if await self.send_message(chat_id, message):
                success_count += 1
            await delay_manager.message_delay()
        
        logger.info(f"✅ Message spam completed: {success_count}/{times} sent")
        return success_count
    
    async def keep_alive(self):
        """Send heartbeat to keep connection alive"""
        while self.running:
            try:
                packet = FFProtocol.create_heartbeat_packet()
                await self.tcp_conn.send_packet(packet)
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            except Exception as e:
                logger.error(f"Keep alive error: {e}")
                break
