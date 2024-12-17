# File: Framework/state_machine_controller.py

class StateMachineController:
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.current_state = "INIT"

    def process_warning_letter(self, warning_letter):
        self.agent_manager.set_context({"warning_letter": warning_letter})
        result = conversation_workflow(self.agent_manager)
        return result