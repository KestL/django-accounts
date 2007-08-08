class MockGateway:
    """
    A mock gateway so that we don't have to call the
    real gateway during testing.
    """
    def __init__(self):
        self.reset()
        
    def start_payment(self, **kwargs):
        self.start_payment_called = True
        return self._respond(kwargs.get('error'), '1000')
    
    def change_payment(self, **kwargs):
        self.change_payment_called = True
        return self._respond(kwargs.get('error'), True)
    
    def cancel_payment(self, **kwargs):
        self.cancel_payment_called = True
        return self._respond(kwargs.get('error'), True)
    
    def _respond(self, error=None, value=None):
        if error or self.error:
            raise (error or self.error)('')
        else:
            return value
        
    def reset(self):
        self.error = None
        self.start_payment_called = False
        self.change_payment_called = False
        self.cancel_payment_called = False

