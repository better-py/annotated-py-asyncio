# annotated-py-asyncio
asyncio 源码注解.

- [asyncio](https://github.com/python/asyncio)
- python 3.3 版本, 添加此库, 
- python 3.4 版本之后, 被添加到标准库中.


## 版本说明:

- [asyncio-3.4.3](https://github.com/python/asyncio/releases/tag/3.4.3)
    - 发布时间:  5 Feb 2015
    - 阅读时间:  2017-02-21



## 源码结构:


```text

-> % tree asyncio -L 1

asyncio
├── __init__.py
├── base_events.py
├── base_subprocess.py
├── constants.py
├── coroutines.py
├── events.py
├── futures.py
├── locks.py
├── log.py
├── proactor_events.py
├── protocols.py
├── queues.py
├── selector_events.py
├── selectors.py
├── sslproto.py
├── streams.py
├── subprocess.py
├── tasks.py
├── test_support.py
├── test_utils.py
├── transports.py
├── unix_events.py
├── windows_events.py
└── windows_utils.py

0 directories, 24 files


```


## 阅读顺序:

- 由示例代码开始阅读, 然后找到 lib 入口.

- [examples/hello_coroutine.py](./asyncio-3.4.3/examples/hello_coroutine.py)
    - get_event_loop()
        - 定位到: [asyncio/events.py](./asyncio-3.4.3/asyncio/events.py)
        - asyncio.events.get_event_loop()

