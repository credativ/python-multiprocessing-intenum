# Python multiprocessing-intenum

`IntEnumValue` is an implementation of a multiprocessing safe shared object
for `IntEnum` enum values.

The `IntEnumValue` appears and can be used much like an `IntEnum`, while
internally, it uses a `multiprocessing.Value` shared ctypes integer object
to store the integer value of the enum in a multiprocessing safe way.

It is fully typed and implemented as a generic class, thus allowing to guard
against programming errors where values other than the designated
specific `IntEnum` type are being assigned.

## License

Copyright (C) 2024-2025 credativ GmbH https://www.credativ.de/en/

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Installation

1. Install required packages, e.g. on Debian GNU/Linux:
```
apt-get install git python3
```

1. Install uv from https://github.com/astral-sh/uv/releases

1. Setup and activate Python virtual environment:
   ```
   uv venv --prompt='mp-intenum'
   . .venv/bin/activate
   ```

1. Install Python requirements in the virtual environment::
   ```
   uv sync --locked
   ```

1. Build:
   ```
   make dist
   ```

### Development

* Run code quality checks:
```
make lint
```

* Run test suite:
```
make test
```

## Usage

### Example

To illustrate the usage, an example of a multithreaded worker is used, which
has an internal state represented as an enum that should be tracked across
its threads.

To use a multiprocessing safe `IntEnum`, first define the actual underlying
`IntEnum` type:

```
class WorkerStatusEnum(IntEnum):
    UNAVAILABLE = enum.auto()
    IDLE = enum.auto()
    CALCULATING = enum.auto()
```

`IntEnumValue` is a generic class, accepting a type parameter for the type
of the underlying `IntEnum`.
Thus define the corresponding `IntEnumValue` type for that `IntEnum` like
this:

```
class WorkerStatus(IntEnumValue[WorkerStatusEnum]):
    pass
```

Now this `WorkerStatus` type can be used like an enum to track the state:

```
>>> status = WorkerStatus(WorkerStatusEnum.IDLE)
>>> status.name
'IDLE'
>>> status.value
2
>>> with status.get_lock():
...     status.set(WorkerStatusEnum.CALCULATING)
>>> status.name
'CALCULATING'
>>> status.value
3
```

It can, of course, also be wrapped in a dedicated class, which the remaining
examples will further expand on:

```
class WorkerState:
    def __init__(self) -> None:
        self.status = WorkerStatus(WorkerStatusEnum.IDLE)
```

When using multiple `multiprocessing.Value` instances (including
`IntEnumValue` ones) that should share a lock to allow ensuring that they
can only be changed in a consistent state, pass that shared lock as a
keyword argument on instantiation:

```
class WorkerState:
    def __init__(self) -> None:
        self.lock = multiprocessing.RLock()
        self.status = WorkerStatus(WorkerStatusEnum.IDLE, lock=self.lock)
        self.job_id = multiprocessing.Value("i", -1, lock=self.lock)

    def get_lock(self) -> Lock | RLock:
        return self.lock
```

To avoid having to call the `set()` method to assign a value to the
`IntEnumValue` attribute, it is suggested to keep the actual
attribute private to the class and implement getter and setter methods for a
public property that hides this implementation detail, e.g. as follows:

```
class WorkerState:
    def __init__(self) -> None:
        self._status = WorkerStatus(WorkerStatusEnum.IDLE)

    @property
    def status(self) -> WorkerStatusEnum:
        return self._status  # type: ignore[return-value]

    @status.setter
    def status(self, status: WorkerStatusEnum | str) -> None:
        self._status.set(status)
```

This can be used in a more elegant manner by simply assigning to the status
attribute:

```
>>> state = WorkerState()
>>> state.status.name
'IDLE'
>>> with state.get_lock():
...     state.status = WorkerStatusEnum.CALCULATING
>>> state.status.name
'CALCULATING'
```

The specific `IntEnumValue` type can override methods to add further
functionality.
A common example is overriding the `set()` method to add logging:

```
class WorkerStatus(IntEnumValue[WorkerStatusEnum]):
    def set(self, value: WorkerStatusEnum | str) -> None:
        super().set(value)
        logger.info(f"WorkerStatus set to '{self.name}'")
```
