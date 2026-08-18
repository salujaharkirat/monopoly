from typing import Dict, List, Callable, Any, Awaitable

class EventBus:
  """Central event bus for WebSocket messages"""
  
  _handlers: Dict[str, List[Callable]] = {}
  
  @classmethod
  def subscribe(cls, event_type: str):
    """Decorator to subscribe to events"""
    def decorator(func: Callable[[Any, dict], Awaitable[None]]):
        if event_type not in cls._handlers:
            cls._handlers[event_type] = []
        cls._handlers[event_type].append(func)
        return func
    return decorator
  
  @classmethod
  async def publish(cls, consumer, event_type: str, data: dict):
    """Publish an event to all subscribers"""
    if event_type not in cls._handlers:
        return
    
    for handler in cls._handlers[event_type]:
        await handler(consumer, data)