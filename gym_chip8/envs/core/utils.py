class Singleton(type):
    _inst = {}

    def __call__(klass, *args, **kwargs):
        if klass not in klass._inst:
            klass._inst[klass] = super(Singleton, klass).__call__(*args, **kwargs)
        return klass._inst[klass]
