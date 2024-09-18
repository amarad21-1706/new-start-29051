def serialize_step(step):
    return {
        "step_id": step.id,  # Basic field
        "step_name": step.name  # Basic field
        # add more fields
    }

def serialize_workflow(workflow):
    return {
        "workflow_id": workflow.id,  # Basic field
        "workflow_name": workflow.name  # Basic field
        # add more fields
    }

