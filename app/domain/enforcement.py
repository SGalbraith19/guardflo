class EnforcementError(Exception):

   def __init__(self, decision_or_message):
       if isinstance(decision_or_message, str):
           self.reason = decision_or_message
           super().__init__(decision_or_message)
       else:
           # Decision object
           self.reason = decision_or_message.reason
           self.decision = decision_or_message
           super().__init__(decision_or_message.reason)