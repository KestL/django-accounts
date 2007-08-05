class PaymentRequestError(Exception):
    """
    Exception raised when the data sent to
    the payment gateway was not valid.
    """
    def __init__(self, messages):
        self.messages = messages
    def __str__(self):
        return str(self.messages)
    
class PaymentResponseError(Exception):
    """
    Exception raised when the data recieved
    from the payment gateway was not valid.
    """
    def __init__(self, response):
        self.response = response
    def __str__(self):
        return str(self.response)
