# 程序入口文件，启动主引擎和代理调度
# TODO: Implement logic here
# main.py

#!/usr/bin/env python3
"""
PersonalAI 主入口文件
负责初始化系统、加载配置、启动引擎和调度代理

架构说明：
1. 加载配置文件 (config/)
2. 初始化核心引擎 (src/core/)
3. 加载模块 (src/modules/)
4. 注册触发器 (triggers/)
5. 启动主循环
"""

import os
import sys
import signal
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 添加项目根目录到 Python 路径
ROOT_PATH = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_PATH))

from src.core.engine import CoreEngine
from src.core.wiki_manager import WikiManager
from src.core.security import SecurityManager
from src.modules.loader import ModuleLoader
from agents.reflection_agent import ReflectionAgent
from agents.consolidator import MemoryConsolidator
from agents.maintenance_agent import MaintenanceAgent
from triggers import TriggerLoader
from config.config_loader import ConfigLoader
from src.utils.logger import setup_logger, get_logger
from tools.audit_trail import AuditTrailer
# 初始化日志
logger = setup_logger("Main", str(ROOT_PATH / "data" / "main.log"))

class PersonalAI:
    """
    PersonalAI 主类
    管理整个系统的生命周期
    """
    
    def __init__(self):
        self.root_path = ROOT_PATH
        self.config_loader = ConfigLoader(str(self.root_path))
        self.engine: Optional[CoreEngine] = None
        self.trigger_loader: Optional[TriggerLoader] = None
        self.running = False
        
    def initialize(self):
        """
        初始化系统组件
        """
        logger.info("Initializing PersonalAI...")
        
        # 1. 加载配置
        config = self.config_loader.get_system_config()
        logger.info(f"Loaded system config: security_level={config.get('security', {}).get('level')}")
        
        # 2. 初始化安全模块
        security = SecurityManager(str(self.root_path))
        logger.info("SecurityManager initialized")
        
        # 3. 初始化 Wiki 管理器
        wiki_manager = WikiManager(str(self.root_path), security)
        logger.info("WikiManager initialized")
        
        # 4. 初始化核心引擎 (需要注入 LLM 客户端)
        llm_client = self._create_llm_client(config)
        self.engine = CoreEngine(str(self.root_path), llm_client)
        logger.info("CoreEngine initialized")
        
        # 5. 加载模块
        module_loader = ModuleLoader()
        modules = module_loader.load_all()
        logger.info(f"Loaded {len(modules)} modules")
        
        # 6. 加载触发器
        self.trigger_loader = TriggerLoader(str(self.root_path))
        triggers = self.trigger_loader.load_all()
        logger.info(f"Loaded {len(triggers)} triggers")
        
        # 7. 初始化代理
        self.reflection_agent = ReflectionAgent(str(self.root_path), llm_client, wiki_manager)
        self.consolidator = MemoryConsolidator(str(self.root_path), llm_client, wiki_manager)
        self.maintenance_agent = MaintenanceAgent(str(self.root_path), wiki_manager)
        logger.info("Agents initialized")
        
        logger.info("PersonalAI initialization complete")
        # 确保 tools/audit_trail.py 被正确调用
        self.auditor = AuditTrailer(str(self.root_path))
    
    
    def _create_llm_client(self, config: Dict) -> Any:
        """
        创建 LLM 客户端
        :param config: 系统配置
        :return: LLM 客户端实例
        """
        import os
        from dotenv import load_dotenv
    
        # 加载环境变量
        load_dotenv()
        
        api_key = os.getenv('LLM_API_KEY')
        model = os.getenv('LLM_MODEL', 'gpt-4o')
        base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
        
        # 如果没有 API Key，使用 Mock
        if not api_key or api_key == 'sk-your-api-key-here':
            print("⚠️  未配置真实 API Key，使用 Mock 模式")
            return self._create_mock_llm()
        
        try:
            # 使用 OpenAI SDK
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
            
            # 包装成统一的 generate 接口
            class OpenAIWrapper:
                def __init__(self, client, model):
                    self.client = client
                    self.model = model
                    
                def generate(self, prompt: str) -> str:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=2048
                    )
                    return response.choices[0].message.content
                    
            print(f"✅ 已连接真实 LLM: {model}")
            return OpenAIWrapper(client, model)
            
        except ImportError:
            print("⚠️  未安装 openai 库，使用 Mock 模式")
            print("   运行：pip install openai")
            return self._create_mock_llm()
        except Exception as e:
            print(f"⚠️  LLM 连接失败：{e}，使用 Mock 模式")
            return self._create_mock_llm()
            
    def _create_mock_llm(self):
        """创建 Mock LLM 客户端"""
        class MockLLM:
            def generate(self, prompt: str) -> str:
                return f"[Mock Response] 收到 {len(prompt)} 字符的提示"
        return MockLLM()

        
    def start_session(self) -> str:
        """
        启动新会话
        :return: 会话 ID
        """
        if not self.engine:
            raise RuntimeError("Engine not initialized")
        session_id = self.engine.start_session()
        logger.info(f"Session started: {session_id}")
        return session_id
        
    def process_input(self, user_input: str) -> str:
        """
        处理用户输入
        :param user_input: 用户文本
        :return: AI 响应
        """
        if not self.engine:
            raise RuntimeError("Engine not initialized")
        response = self.engine.process_input(user_input)
        logger.info(f"Processed input: {user_input[:50]}...")
        return response
        
    # 修改 main.py 的 end_session 方法

    def end_session(self):
        """
        结束当前会话，触发反思代理
        """
        if not self.engine:
            return
        self.engine.end_session()
    
        # 触发反思代理
        triggers = self.trigger_loader.get_triggers_by_event('session_end')
        for trigger in triggers:
            self._execute_trigger(trigger)
    
        # 直接调用 ReflectionAgent (确保执行)
        if hasattr(self, 'reflection_agent') and self.engine.session_id:
            try:
                archive_path = self.root_path / 'wiki' / '06_Raw_Archives' / datetime.now().strftime("%Y-%m") / f"{self.engine.session_id}_raw.md"
                if archive_path.exists():
                    self.reflection_agent.run(self.engine.session_id, str(archive_path))
                    print("✅ 反思日志已生成")
            except Exception as e:
                print(f"❌ 反思失败：{e}")
    
        logger.info("Session ended, reflection triggered")

        
    def _execute_trigger(self, trigger: Dict):
        """
        执行触发器配置的动作
        :param trigger: 触发器配置
        """
        logger.info(f"Executing trigger: {trigger.get('trigger_name')}")
        for action in trigger.get('actions', []):
            try:
                if action['type'] == 'agent':
                    agent_class = action['class']
                    method = action['method']
                    agent = getattr(self, agent_class.lower(), None)
                    if agent and hasattr(agent, method):
                        getattr(agent, method)()
                elif action['type'] == 'tool':
                    # 工具调用逻辑
                    pass
            except Exception as e:
                logger.error(f"Trigger action failed: {e}")
                
    def run_idle_maintenance(self):
        """
        运行空闲维护任务
        """
        triggers = self.trigger_loader.get_triggers_by_event('idle')
        for trigger in triggers:
            self._execute_trigger(trigger)
            
    def shutdown(self):
        """
        安全关闭系统
        """
        logger.info("Shutting down PersonalAI...")
        self.running = False
        # 保存状态、关闭连接等
        logger.info("PersonalAI shutdown complete")
        
def signal_handler(sig, frame):
    """处理中断信号"""
    logger.info("Received interrupt signal")
    if 'ai' in globals():
        ai.shutdown()
    sys.exit(0)

# 全局实例
ai: Optional[PersonalAI] = None

def main():
    """主函数"""
    global ai
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 初始化系统
        ai = PersonalAI()
        ai.initialize()
        
        # 启动主循环 (示例：命令行交互)
        ai.running = True
        print("=" * 50)
        print("PersonalAI 已启动")
        print("输入 'quit' 退出，输入 'end' 结束当前会话")
        print("=" * 50)
        
        # 启动初始会话
        session_id = ai.start_session()
        print(f"会话 ID: {session_id}")
        
        while ai.running:
            try:
                user_input = input("\n用户：").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    ai.end_session()
                    break
                elif user_input.lower() == 'end':
                    ai.end_session()
                    session_id = ai.start_session()
                    print(f"新会话 ID: {session_id}")
                    continue
                elif not user_input:
                    continue
                    
                response = ai.process_input(user_input)
                print(f"AI: {response}")
                
            except KeyboardInterrupt:
                continue
            except Exception as e:
                logger.error(f"Error processing input: {e}")
                print(f"错误：{e}")
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        if ai:
            ai.shutdown()

if __name__ == "__main__":
    main()
