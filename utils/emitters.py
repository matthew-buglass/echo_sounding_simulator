import abc


class VectorEmitter:
    @abc.abstractmethod
    def emit_vector(self, vector):
        raise NotImplementedError("You must override emit_vector()")


class StdOutVectorEmitter(VectorEmitter):
    def emit_vector(self, vector):
        print(vector)

