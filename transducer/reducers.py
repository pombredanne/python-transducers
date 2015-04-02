from transducer.infrastructure import Reducer, Reduced
from transducer.sinks import null_sink


class Appending(Reducer):

    def initial(self):
        return []

    def step(self, result, item):
        result.append(item)
        return result

    def combine(self, left, right):
        left.extend(right)
        return left

_appending = Appending()


def appending():
    return _appending


class Conjoining(Reducer):

    def initial(self):
        return tuple()

    def step(self, result, item):
        return result + type(result)((item,))

    def combine(self, left, right):
        return left + right

_conjoining = Conjoining()


def conjoining():
    return _conjoining


class Concatenating(Reducer):

    def initial(self):
        return ""

    def step(self, result, item):
        return result + item

    def combine(self, left, right):
        return self.step(left, right)

_concatenating = Concatenating()


def concatenating():
    return _concatenating


class Extending(Reducer):

    def initial(self):
        return []

    def step(self, result, item):
        result.extend(item)
        return result

    def combine(self, left, right):
        return self.step(left, right)

_extending = Extending()


def extending():
    return _extending


class Adding(Reducer):

    def initial(self):
        return set()

    def step(self, result, item):
        result.add(item)
        return result

    def combine(self, left, right):
        left |= right
        return left

_adding = Adding()


def adding():
    return _adding


class ExpectingSingle(Reducer):

    def __init__(self):
        self._num_steps = 0

    def initial(self):
        return None

    def step(self, result, item):
        self._num_steps += 1
        if self._num_steps > 1:
            raise RuntimeError("Too many steps!")
        assert result is None
        return item

    def complete(self, result):
        if self._num_steps < 1:
            raise RuntimeError("Too few steps!")
        return result


def expecting_single():
    return ExpectingSingle()


class Sending(Reducer):

    def initial(self):
        return null_sink()

    def step(self, result, item):
        try:
            result.send(item)
        except StopIteration:
            return Reduced(result)
        else:
            return result

    def complete(self, result):
        result.close()
        return result

_sending = Sending()


def sending():
    return _sending


class Completing(Reducer):

    def __init__(self, reducer, identity, combiner):
        self._reducer = reducer
        self._identity = identity
        self._combiner = combiner

    def initial(self):
        return self._identity

    def step(self, result, item):
        return self._reducer(result, item)

    def combine(self, left, right):
        return self._combiner(left, right) if (self._combiner is not None) else super().combine(left, right)


def completing(reducer, identity=None, combiner=None):
    """Complete a regular reducing function to support the Reducer protocol.

    Args:
        reducer: A reducing function. e.g. lambda x, y: x+y
        identity: The identity (i.e. seed) value for reducer. e.g. zero

    Returns:
        An instance of the Completing reducer.
    """

    return Completing(reducer, identity, combiner)
