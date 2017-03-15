#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A Future class similar to the one in PEP 3148.

======================================

# 参考:
- http://www.snarky.ca/how-the-heck-does-async-await-work-in-python-3-5
    - 高质量
    - 译文 [Python 3.5 协程究竟是个啥]:
        - https://juejin.im/entry/56ea295ed342d300546e1e22
        - https://github.com/xitu/gold-miner/blob/master/TODO/how-the-heck-does-async-await-work-in-python-3-5.md
        - http://blog.rainy.im/2016/03/10/how-the-heck-does-async-await-work-in-python-3-5/

======================================

# 补充:

    yield from iterator

    本质上）相当于：

    for x in iterator:
        yield x

======================================

# 协程概念:

- “协程 是为非抢占式多任务产生子程序的计算机程序组件，协程允许不同入口点在不同位置暂停或开始执行程序”。
- 从技术的角度来说，“协程就是你可以暂停执行的函数”。
- 如果你把它理解成“就像生成器一样”，那么你就想对了。


# 事件循环:

- 事件循环 “是一种等待程序分配事件或消息的编程架构”。
- 基本上来说事件循环就是，“当A发生时，执行B”。
- 或许最简单的例子来解释这一概念就是用每个浏览器中都存在的JavaScript事件循环。
- 当你点击了某个东西（“当A发生时”），这一点击动作会发送给JavaScript的事件循环，并检查是否存在注册过的 onclick 回调来处理这一点击（“执行B”）。
- 只要有注册过的回调函数就会伴随点击动作的细节信息被执行。
- 事件循环被认为是一种循环是因为它不停地收集事件并通过循环来发如何应对这些事件。

# Python 的事件循环:

- 对 Python 来说，用来提供事件循环的 asyncio 被加入标准库中。
- asyncio 重点解决网络服务中的问题，事件循环在这里将来自套接字（socket）的 I/O 已经准备好读和/或写作为“当A发生时”（通过selectors模块）。
- 除了 GUI 和 I/O，事件循环也经常用于在别的线程或子进程中执行代码，并将事件循环作为调节机制（例如，合作式多任务）。
- 如果你恰好理解 Python 的 GIL，事件循环对于需要释放 GIL 的地方很有用。

- 事件循环提供一种循环机制，让你可以“在A发生时，执行B”。
- 基本上来说事件循环就是监听当有什么发生时，同时事件循环也关心这件事并执行相应的代码。
- Python 3.4 以后通过标准库 asyncio 获得了事件循环的特性。


# asyncio.Future对象:

- 有了对协程明确的定义（能够匹配生成器所提供的API），你可以对任何asyncio.Future对象使用 yield from，
- 从而将其传递给事件循环，暂停协程的执行来等待某些事情的发生（ future 对象并不重要，只是asyncio细节的实现）。
- 一旦 future 对象获取了事件循环，它会一直在那里监听，直到完成它需要做的一切。
- 当 future 完成自己的任务之后，事件循环会察觉到，暂停并等待在那里的协程会通过send()方法获取future对象的返回值并开始继续执行。


# Future对象 使用示例:

- 事件循环启动每一个 countdown() 协程，一直执行到遇见其中一个协程的 yield from 和 asyncio.sleep() 。
- 这样会返回一个 asyncio.Future对象并将其传递给事件循环，同时暂停这一协程的执行。
- 事件循环会监控这一future对象，直到倒计时1秒钟之后（同时也会检查其它正在监控的对象，比如像其它协程）。
- 1秒钟的时间一到，事件循环会选择刚刚传递了future对象并暂停了的 countdown() 协程，将future对象的结果返回给协程，然后协程可以继续执行。
- 这一过程会一直持续到所有的 countdown() 协程执行完毕，事件循环也被清空。
- 稍后我会给你展示一个完整的例子，用来说明协程/事件循环之类的这些东西究竟是如何运作的，但是首先我想要解释一下async和await。

======================================


# 在 Python 3.4 中，用于异步编程并被标记为协程的函数看起来是这样的：

    # This also works in Python 3.5.
    @asyncio.coroutine
    def py34_coro():
        yield from stuff()

======================================


Python 3.5 添加了types.coroutine 修饰器，也可以像 asyncio.coroutine 一样将生成器标记为协程。
你可以用 async def 来定义一个协程函数，虽然这个函数不能包含任何形式的 yield 语句；只有 return 和 await 可以从协程中返回值。

    async def py35_coro():
        await stuff()


你将发现不仅仅是 async，Python 3.5 还引入 await 表达式（只能用于async def中）。
虽然await的使用和yield from很像，但await可以接受的对象却是不同的。
await 当然可以接受协程，因为协程的概念是所有这一切的基础。
但是当你使用 await 时，其接受的对象必须是awaitable 对象：必须是定义了__await__()方法且这一方法必须返回一个不是协程的迭代器。
协程本身也被认为是 awaitable 对象（这也是collections.abc.Coroutine 继承 collections.abc.Awaitable的原因）。
这一定义遵循 Python 将大部分语法结构在底层转化成方法调用的传统，就像 a + b 实际上是a.__add__(b) 或者 b.__radd__(a)。


为什么基于async的协程和基于生成器的协程会在对应的暂停表达式上面有所不同？
主要原因是出于最优化Python性能的考虑，确保你不会将刚好有同样API的不同对象混为一谈。
由于生成器默认实现协程的API，因此很有可能在你希望用协程的时候错用了一个生成器。
而由于并不是所有的生成器都可以用在基于协程的控制流中，你需要避免错误地使用生成器。



用async def可以定义得到协程。
定义协程的另一种方式是通过types.coroutine修饰器
    -- 从技术实现的角度来说就是添加了 CO_ITERABLE_COROUTINE标记
    -- 或者是collections.abc.Coroutine的子类。
你只能通过基于生成器的定义来实现协程的暂停。



awaitable 对象要么是一个协程要么是一个定义了__await__()方法的对象
    -- 也就是collections.abc.Awaitable
    -- 且__await__()必须返回一个不是协程的迭代器。


await表达式基本上与 yield from 相同但只能接受awaitable对象（普通迭代器不行）。
async定义的函数要么包含return语句
    -- 包括所有Python函数缺省的return None
    -- 和/或者 await表达式（yield表达式不行）。
async函数的限制确保你不会将基于生成器的协程与普通的生成器混合使用，因为对这两种生成器的期望是非常不同的。


======================================


# 将 async/await 看做异步编程的 API

- David 的意思是人们不应该将async/await等同于asyncio，
- 而应该将asyncio看作是一个利用async/await API 进行异步编程的框架。
- David 将 async/await 看作是异步编程的API创建了 curio 项目来实现他自己的事件循环。
    - 项目地址: https://github.com/dabeaz/curio
    - 允许像 curio 一样的项目不仅可以在较低层面上拥有不同的操作方式
    -（例如 asyncio 利用 future 对象作为与事件循环交流的 API，而 curio 用的是元组）


- 异步库参考:
    - https://github.com/Lukasa/hyper

======================================

# 总结:

基本上 async 和 await 产生神奇的生成器，我们称之为协程，
同时需要一些额外的支持例如 awaitable 对象以及将普通生成器转化为协程。
所有这些加到一起来支持并发，这样才使得 Python 更好地支持异步编程。
相比类似功能的线程，这是一个更妙也更简单的方法。

======================================

# 关于 python 协程 和 golang 的对比讨论:

- https://news.ycombinator.com/item?id=10402307
- https://docs.google.com/presentation/d/1LO_WI3N-3p2Wp9PDWyv5B6EGFZ8XTOTNJ7Hd40WOUHo/mobilepresent?pli=1&slide=id.g70b0035b2_1_154
    - 关于此PPT 的观点:  go 比pypy 性能高不了多少, 但是复杂度和调试难度增加很高
    - 结尾鼓吹 rust.
======================================


"""

__all__ = ['CancelledError', 'TimeoutError',
           'InvalidStateError',
           'Future', 'wrap_future',
           ]

import concurrent.futures._base       # 注意
import logging
import reprlib
import sys
import traceback


#
# 唯一依赖:
#
from . import events       # 注意

# States for Future.
_PENDING = 'PENDING'
_CANCELLED = 'CANCELLED'
_FINISHED = 'FINISHED'

_PY34 = sys.version_info >= (3, 4)

Error = concurrent.futures._base.Error
CancelledError = concurrent.futures.CancelledError
TimeoutError = concurrent.futures.TimeoutError

STACK_DEBUG = logging.DEBUG - 1  # heavy-duty debugging


class InvalidStateError(Error):
    """The operation is not allowed in this state."""


class _TracebackLogger:
    """Helper to log a traceback upon destruction if not cleared.

    This solves a nasty problem with Futures and Tasks that have an
    exception set: if nobody asks for the exception, the exception is
    never logged.  This violates the Zen of Python: 'Errors should
    never pass silently.  Unless explicitly silenced.'

    However, we don't want to log the exception as soon as
    set_exception() is called: if the calling code is written
    properly, it will get the exception and handle it properly.  But
    we *do* want to log it if result() or exception() was never called
    -- otherwise developers waste a lot of time wondering why their
    buggy code fails silently.

    An earlier attempt added a __del__() method to the Future class
    itself, but this backfired because the presence of __del__()
    prevents garbage collection from breaking cycles.  A way out of
    this catch-22 is to avoid having a __del__() method on the Future
    class itself, but instead to have a reference to a helper object
    with a __del__() method that logs the traceback, where we ensure
    that the helper object doesn't participate in cycles, and only the
    Future has a reference to it.

    The helper object is added when set_exception() is called.  When
    the Future is collected, and the helper is present, the helper
    object is also collected, and its __del__() method will log the
    traceback.  When the Future's result() or exception() method is
    called (and a helper object is present), it removes the helper
    object, after calling its clear() method to prevent it from
    logging.

    One downside is that we do a fair amount of work to extract the
    traceback from the exception, even when it is never logged.  It
    would seem cheaper to just store the exception object, but that
    references the traceback, which references stack frames, which may
    reference the Future, which references the _TracebackLogger, and
    then the _TracebackLogger would be included in a cycle, which is
    what we're trying to avoid!  As an optimization, we don't
    immediately format the exception; we only do the work when
    activate() is called, which call is delayed until after all the
    Future's callbacks have run.  Since usually a Future has at least
    one callback (typically set by 'yield from') and usually that
    callback extracts the callback, thereby removing the need to
    format the exception.

    PS. I don't claim credit for this solution.  I first heard of it
    in a discussion about closing files when they are collected.
    """

    __slots__ = ('loop', 'source_traceback', 'exc', 'tb')

    def __init__(self, future, exc):
        self.loop = future._loop
        self.source_traceback = future._source_traceback
        self.exc = exc
        self.tb = None

    def activate(self):
        exc = self.exc
        if exc is not None:
            self.exc = None
            self.tb = traceback.format_exception(exc.__class__, exc,
                                                 exc.__traceback__)

    def clear(self):
        self.exc = None
        self.tb = None

    def __del__(self):
        if self.tb:
            msg = 'Future/Task exception was never retrieved\n'
            if self.source_traceback:
                src = ''.join(traceback.format_list(self.source_traceback))
                msg += 'Future/Task created at (most recent call last):\n'
                msg += '%s\n' % src.rstrip()
            msg += ''.join(self.tb).rstrip()
            self.loop.call_exception_handler({'message': msg})


#########################################
#             Future 类
#
# 说明:
#   - 关键类
#   - 其他模块依赖此模块:
#       - BaseEventLoop() 实现, 依赖此模块
#       - Task() 实现, 依赖此模块
#       - 实现协程装饰器, 依赖此模块
#
#########################################
class Future:
    """This class is *almost* compatible with concurrent.futures.Future.

    Differences:

    - result() and exception() do not take a timeout argument and
      raise an exception when the future isn't done yet.

    - Callbacks registered with add_done_callback() are always called
      via the event loop's call_soon_threadsafe().

    - This class is not compatible with the wait() and as_completed()
      methods in the concurrent.futures package.

    (In Python 3.4 or later we may be able to unify the implementations.)
    """

    # Class variables serving as defaults for instance variables.
    _state = _PENDING
    _result = None
    _exception = None
    _loop = None
    _source_traceback = None

    _blocking = False  # proper use of future (yield vs yield from)

    _log_traceback = False   # Used for Python 3.4 and later
    _tb_logger = None        # Used for Python 3.3 only

    def __init__(self, *, loop=None):
        """Initialize the future.

        The optional event_loop argument allows to explicitly set the event
        loop object used by the future. If it's not provided, the future uses
        the default event loop.
        """
        if loop is None:
            self._loop = events.get_event_loop()      # 事件循环
        else:
            self._loop = loop

        self._callbacks = []     # 回调

        if self._loop.get_debug():
            self._source_traceback = traceback.extract_stack(sys._getframe(1))

    def _format_callbacks(self):
        cb = self._callbacks
        size = len(cb)
        if not size:
            cb = ''

        def format_cb(callback):
            return events._format_callback(callback, ())

        if size == 1:
            cb = format_cb(cb[0])
        elif size == 2:
            cb = '{}, {}'.format(format_cb(cb[0]), format_cb(cb[1]))
        elif size > 2:
            cb = '{}, <{} more>, {}'.format(format_cb(cb[0]),
                                            size-2,
                                            format_cb(cb[-1]))
        return 'cb=[%s]' % cb

    def _repr_info(self):
        info = [self._state.lower()]
        if self._state == _FINISHED:
            if self._exception is not None:
                info.append('exception={!r}'.format(self._exception))
            else:
                # use reprlib to limit the length of the output, especially
                # for very long strings
                result = reprlib.repr(self._result)
                info.append('result={}'.format(result))
        if self._callbacks:
            info.append(self._format_callbacks())
        if self._source_traceback:
            frame = self._source_traceback[-1]
            info.append('created at %s:%s' % (frame[0], frame[1]))
        return info

    def __repr__(self):
        info = self._repr_info()
        return '<%s %s>' % (self.__class__.__name__, ' '.join(info))

    # On Python 3.3 and older, objects with a destructor part of a reference
    # cycle are never destroyed.
    # It's not more the case on Python 3.4 thanks to the PEP 442.
    if _PY34:
        def __del__(self):
            if not self._log_traceback:
                # set_exception() was not called, or result() or exception()
                # has consumed the exception
                return
            exc = self._exception
            context = {
                'message': ('%s exception was never retrieved'
                            % self.__class__.__name__),
                'exception': exc,
                'future': self,
            }
            if self._source_traceback:
                context['source_traceback'] = self._source_traceback
            self._loop.call_exception_handler(context)

    ############################################################
    #                    接口定义
    ############################################################

    # 取消 future 对象
    #   - 若 future 已完成, 或者已取消, 返回 FALSE
    #   - 否则, 改变 future 状态为可取消, 并计划执行回调
    def cancel(self):
        """Cancel the future and schedule callbacks.

        If the future is already done or cancelled, return False.  Otherwise,
        change the future's state to cancelled, schedule the callbacks and
        return True.
        """
        if self._state != _PENDING:
            return False
        self._state = _CANCELLED    # 状态置为: 可取消
        self._schedule_callbacks()  # 计划执行回调
        return True

    #
    # 计划执行回调:
    #   - 请求事件循环, 去调用所有的回调
    #   - 这些回调, 原本计划为立即被调用, 同时从回调列表中清除
    #
    def _schedule_callbacks(self):
        """Internal: Ask the event loop to call all callbacks.

        The callbacks are scheduled to be called as soon as possible. Also
        clears the callback list.
        """
        callbacks = self._callbacks[:]   # 临时变量, 暂存回调列表
        if not callbacks:
            return

        self._callbacks[:] = []          # 清空回调列表

        #
        # 执行所有的回调
        #
        for callback in callbacks:
            self._loop.call_soon(callback, self)   # 计划执行回调

    #
    # 状态判断:
    #   - future 对象: 取消状态
    #
    def cancelled(self):
        """Return True if the future was cancelled."""
        return self._state == _CANCELLED

    # Don't implement running(); see http://bugs.python.org/issue18699

    #
    # 状态判断:
    #   - future 对象: 完成状态
    #
    def done(self):
        """Return True if the future is done.

        Done means either that a result / exception are available, or that the
        future was cancelled.
        """
        return self._state != _PENDING

    #
    # future 的返回结果
    #
    def result(self):
        """Return the result this future represents.

        3种情况:
            If the future has been cancelled, raises CancelledError.
            If the future's result isn't yet available, raises InvalidStateError.
            If the future is done and has an exception set, this exception is raised.
        """
        # 异常: future 已取消
        if self._state == _CANCELLED:
            raise CancelledError

        # 异常: future 暂不可获得
        if self._state != _FINISHED:
            raise InvalidStateError('Result is not ready.')

        self._log_traceback = False
        if self._tb_logger is not None:
            self._tb_logger.clear()
            self._tb_logger = None

        # 异常: future 已完成
        if self._exception is not None:
            raise self._exception   # 异常结果
        return self._result         # future 已完成, 正常返回结果

    #
    # future 返回一个异常
    #   - 触发本异常的条件: future 完成状态下
    #
    def exception(self):
        """Return the exception that was set on this future.

        The exception (or None if no exception was set) is returned only if
        the future is done.

        If the future has been cancelled, raises CancelledError.
        If the future isn't done yet, raises InvalidStateError.
        """
        # 异常: 已取消
        if self._state == _CANCELLED:
            raise CancelledError

        # 异常: 暂未完成
        if self._state != _FINISHED:
            raise InvalidStateError('Exception is not set.')

        self._log_traceback = False
        if self._tb_logger is not None:
            self._tb_logger.clear()
            self._tb_logger = None
        return self._exception     # 返回异常

    #
    # 当 future 完成时, 添加一个回调等待执行
    #
    def add_done_callback(self, fn):
        """Add a callback to be run when the future becomes done.

        The callback is called with a single argument - the future object. If
        the future is already done when this is called, the callback is
        scheduled with call_soon.
        """
        if self._state != _PENDING:
            self._loop.call_soon(fn, self)  # 执行
        else:
            self._callbacks.append(fn)      # 添加一个回调

    # New method not in PEP 3148.

    #
    # 删除回调:
    #
    def remove_done_callback(self, fn):
        """Remove all instances of a callback from the "call when done" list.

        Returns the number of callbacks removed.
        """
        filtered_callbacks = [f for f in self._callbacks if f != fn]     # 过滤回调
        removed_count = len(self._callbacks) - len(filtered_callbacks)
        if removed_count:
            self._callbacks[:] = filtered_callbacks    # 更新原回调列表为: 新过滤的
        return removed_count

    # So-called internal methods (note: no set_running_or_notify_cancel()).

    #
    # 当 future 未取消时, 设置 result 结果
    #
    def _set_result_unless_cancelled(self, result):
        """Helper setting the result only if the future was not cancelled."""
        if self.cancelled():
            return
        self.set_result(result)   # 设置future返回结果

    #
    # 标记 future 对象为完成状态, 并设置其返回结果
    #
    def set_result(self, result):
        """Mark the future done and set its result.

        If the future is already done when this method is called, raises
        InvalidStateError.
        """
        if self._state != _PENDING:
            raise InvalidStateError('{}: {!r}'.format(self._state, self))

        self._result = result        # 返回结果
        self._state = _FINISHED      # future 对象: 完成状态
        self._schedule_callbacks()   # 按计划执行回调

    #
    # 标记 future 对象为完成状态, 并触发一个异常
    #
    def set_exception(self, exception):
        """Mark the future done and set an exception.

        If the future is already done when this method is called, raises
        InvalidStateError.
        """
        if self._state != _PENDING:
            raise InvalidStateError('{}: {!r}'.format(self._state, self))
        if isinstance(exception, type):
            exception = exception()

        self._exception = exception   # 返回结果: 异常
        self._state = _FINISHED       # future 对象: 完成状态
        self._schedule_callbacks()    # 按计划执行回调

        if _PY34:
            self._log_traceback = True
        else:
            self._tb_logger = _TracebackLogger(self, exception)
            # Arrange for the logger to be activated after all callbacks
            # have had a chance to call result() or exception().
            self._loop.call_soon(self._tb_logger.activate)

    # Truly internal methods.

    #
    # 从另外一个 future 对象拷贝状态
    #
    def _copy_state(self, other):
        """Internal helper to copy state from another Future.

        The other Future may be a concurrent.futures.Future.
        """
        assert other.done()
        if self.cancelled():
            return
        assert not self.done()
        if other.cancelled():
            self.cancel()
        else:
            exception = other.exception()
            if exception is not None:
                self.set_exception(exception)
            else:
                result = other.result()    # 取结果
                self.set_result(result)    # 设置结果

    #
    # 迭代:
    #
    def __iter__(self):
        if not self.done():
            self._blocking = True   # 阻塞
            yield self  # This tells Task to wait for completion.
        assert self.done(), "yield from wasn't used with future"
        return self.result()  # May raise too.  返回


#
# 包裹 future 对象
#
def wrap_future(fut, *, loop=None):
    """Wrap concurrent.futures.Future object."""
    if isinstance(fut, Future):
        return fut
    assert isinstance(fut, concurrent.futures.Future), \
        'concurrent.futures.Future is expected, got {!r}'.format(fut)

    if loop is None:
        loop = events.get_event_loop()
    new_future = Future(loop=loop)     # 创建future对象

    def _check_cancel_other(f):
        if f.cancelled():
            fut.cancel()

    new_future.add_done_callback(_check_cancel_other)    # 添加回调

    #
    # 线程安全
    #
    fut.add_done_callback(
        lambda future: loop.call_soon_threadsafe(
            new_future._copy_state, future))
    return new_future    # 返回future对象
