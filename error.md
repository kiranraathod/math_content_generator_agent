2025-11-12T13:37:32.559203Z [info     ] Starting background run        [langgraph_api.worker] api_variant=local_dev assistant_id=5f298a96-2a0c-552b-822e-82e68c650c72 graph_id=math_content_generator langgraph_api_version=0.5.12 request_id=97c4d93e-1afc-4757-af72-699f0f9eb00b resumable=False run_attempt=1 run_creation_ms=4 run_id=019a7849-28bc-71bc-8106-6855db21b1f1 run_queue_ms=720 run_started_at=2025-11-12T13:37:32.558835+00:00 run_stream_start_ms=0 temporary=False thread_id=dc5c9821-5ae1-436d-a0ea-75c290644c5b thread_name=asyncio_0
LangSmith tracing enabled for project: content_gen
2025-11-12T13:37:32.826873Z [info     ] 2 changes detected             [watchfiles.main] api_variant=local_dev langgraph_api_version=0.5.12 thread_name=MainThread
2025-11-12T13:37:33.207081Z [info     ] 1 change detected              [watchfiles.main] api_variant=local_dev langgraph_api_version=0.5.12 thread_name=MainThread
2025-11-12T13:37:33.270681Z [error    ] Run encountered an error in graph: <class 'KeyError'>('question_type') [langgraph_api.worker] api_variant=local_dev assistant_id=5f298a96-2a0c-552b-822e-82e68c650c72 graph_id=math_content_generator langgraph_api_version=0.5.12 request_id=97c4d93e-1afc-4757-af72-699f0f9eb00b run_attempt=1 run_id=019a7849-28bc-71bc-8106-6855db21b1f1 thread_id=dc5c9821-5ae1-436d-a0ea-75c290644c5b thread_name=MainThread
Traceback (most recent call last):
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph_api\worker.py", line 142, in wrap_user_errors
    await consume(
        stream, run_id, resumable, stream_modes, thread_id=run["thread_id"]
    )
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph_api\stream.py", line 501, in consume
    raise e
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph_api\stream.py", line 484, in consume
    async for mode, payload in stream:
    ...<6 lines>...
        )
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph_api\stream.py", line 369, in astream_state
    event = await wait_if_not_done(anext(stream, sentinel), done)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph_api\asyncio.py", line 
89, in wait_if_not_done
    raise e.exceptions[0] from None
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph\pregel\main.py", line 
3000, in astream
    async for _ in runner.atick(
    ...<13 lines>...
            yield o
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph\pregel\_runner.py", line 410, in atick
    _panic_or_proceed(
    ~~~~~~~~~~~~~~~~~^
        futures.done.union(f for f, t in futures.items() if t is not None),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        timeout_exc_cls=asyncio.TimeoutError,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        panic=reraise,
        ^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph\pregel\_runner.py", line 520, in _panic_or_proceed
    raise exc
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph\pregel\_retry.py", line 137, in arun_with_retry
    return await task.proc.ainvoke(task.input, config)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph\_internal\_runnable.py", line 705, in ainvoke
    input = await asyncio.create_task(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
        step.ainvoke(input, config, **kwargs), context=context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langgraph\_internal\_runnable.py", line 473, in ainvoke
    ret = await self.afunc(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langchain_core\runnables\config.py", line 603, in run_in_executor
    return await asyncio.get_running_loop().run_in_executor(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<2 lines>...
    )
    ^
  File "C:\Users\ratho\AppData\Roaming\uv\python\cpython-3.13.1-windows-x86_64-none\Lib\concurrent\futures\thread.py", line 59, in run
    result = self.fn(*self.args, **self.kwargs)
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\.venv\Lib\site-packages\langchain_core\runnables\config.py", line 594, in wrapper
    return func(*args, **kwargs)
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\workflow.py", line 117, in _generate_question_node      
    result = self.question_service.generate_question(state)
  File "C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\services\question_service.py", line 55, in generate_question
    question_type = state['question_type']
                    ~~~~~^^^^^^^^^^^^^^^^^
KeyError: 'question_type'
During task with name 'generate_question' and id 'bbd2e966-3320-955b-4787-44bb28ed0236'
2025-11-12T13:37:33.396314Z [error    ] Background run failed. Exception: <class 'KeyError'>('question_type') 