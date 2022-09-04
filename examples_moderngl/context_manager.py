import moderngl


class ContextManager:
    ctx = None

    @staticmethod
    def get_default_context(allow_fallback_standalone_context=True) -> moderngl.Context:
        '''
            Default context
        '''

        if ContextManager.ctx is None:
            try:
                ContextManager.ctx = moderngl.create_context()
            except:
                if allow_fallback_standalone_context:
                    ContextManager.ctx = moderngl.create_standalone_context()
                else:
                    raise

        return ContextManager.ctx
