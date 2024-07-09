from torchrl.envs.transforms import ActionMask, Transform
from tensordict.base import TensorDictBase
from torchrl.envs.transforms.utils import (
    _set_missing_tolerance,
)
from torchrl.envs.transforms.transforms import FORWARD_NOT_IMPLEMENTED

class NestedActionMask(Transform):
    def __init__(self, agent_keys, action_key="action", mask_key="action_mask"):
        self.agent_keys = agent_keys
        self.action_key = action_key
        self.mask_key = mask_key

        in_keys = ["action", "action_mask"] + [(a, action_key) for a in agent_keys] + [(a, mask_key) for a in agent_keys]

        super().__init__(
            in_keys=in_keys, out_keys=[], in_keys_inv=[], out_keys_inv=[]
        )

    def forward(self, tensordict: TensorDictBase) -> TensorDictBase:
        raise RuntimeError(FORWARD_NOT_IMPLEMENTED.format(type(self)))

    def _call(self, tensordict: TensorDictBase) -> TensorDictBase:
        parent = self.parent
        if parent is None:
            raise RuntimeError(
                f"{type(self)}.parent cannot be None: make sure this transform is executed within an environment."
            )
        action_spec = self.container.action_spec
        for agent_key in self.agent_keys:
            mask_path = (agent_key, self.mask_key)
            mask = tensordict.get(mask_path)
            print(mask.shape)
            print(action_spec)
            agent_action_path = (agent_key, self.action_key)
            agent_action_spec = action_spec.get(agent_action_path)
            print(agent_action_spec)
            if not isinstance(agent_action_spec, ActionMask.ACCEPTED_SPECS):
                raise ValueError(
                    ActionMask.SPEC_TYPE_ERROR.format(ActionMask.ACCEPTED_SPECS, type(agent_action_spec))
                )
            agent_action_spec.update_mask(mask.to(action_spec.device))
            
        return tensordict

    def _reset(self, tensordict: TensorDictBase, tensordict_reset: TensorDictBase) -> TensorDictBase:
        action_spec = self.container.action_spec
        for agent_key in self.agent_keys:
            mask_path = (agent_key, self.mask_key)
            mask = tensordict.get(mask_path, None)
            print(mask)
            agent_action_path = (agent_key, self.action_key)
            agent_action_spec = action_spec.get(agent_action_path)
            print(agent_action_spec)
            if not isinstance(agent_action_spec, ActionMask.ACCEPTED_SPECS):
                raise ValueError(
                    ActionMask.SPEC_TYPE_ERROR.format(ActionMask.ACCEPTED_SPECS, type(agent_action_spec))
                )
            if mask is not None:
                mask = mask.to(agent_action_spec.device)
            agent_action_spec.update_mask(mask)

         # TODO: Check that this makes sense
        with _set_missing_tolerance(self, True):
            tensordict_reset = self._call(tensordict_reset)
        return tensordict_reset