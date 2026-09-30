# Author: michael-gh1

import bpy
from bpy.types import Operator

from setup_wizard.import_order import NextStepInvoker
from setup_wizard.setup_wizard_operator_base_classes import CustomOperatorProperties
from setup_wizard.utils.mmd_utils import find_head_bone_name

HEAD_DRIVER_OBJECT_NAME = 'Head Driver'
HEAD_ORIGIN_OBJECT_NAME = 'Head Origin'


class GI_OT_SetUpHeadDriver(Operator, CustomOperatorProperties):
    '''Sets up Head Driver'''
    bl_idname = 'genshin.setup_head_driver'
    bl_label = 'Genshin: Setup Head Driver'

    def execute(self, context):
        head_driver_object = bpy.data.objects.get(HEAD_DRIVER_OBJECT_NAME) or bpy.data.objects.get(HEAD_ORIGIN_OBJECT_NAME)
        if not head_driver_object or not head_driver_object.constraints:
            self.report({'WARNING'}, f'Could not find {HEAD_DRIVER_OBJECT_NAME} or its constraints.')
            if self.next_step_idx:
                NextStepInvoker().invoke(
                    self.next_step_idx, 
                    self.invoker_type, 
                    high_level_step_name=self.high_level_step_name,
                    game_type=self.game_type,
                )
            return {'FINISHED'}

        child_of_constraint = head_driver_object.constraints[0]

        armatures = [object for object in bpy.data.objects if object.type == 'ARMATURE']
        if armatures:
            armature = armatures[0]
            for arm in armatures:
                if any(child.type == 'MESH' for child in arm.children):
                    armature = arm
                    break

            head_bone_name = find_head_bone_name(armature.data.bones)
            if head_bone_name:
                self.set_contraint_target_and_bone(child_of_constraint, armature, head_bone_name)
                self.set_inverse(head_driver_object)
                self.report({'INFO'}, f'Head Driver attached to bone: {head_bone_name}')
            else:
                self.report({'WARNING'}, 'Could not automatically identify Head bone.')
        else:
            self.report({'WARNING'}, 'No armature found for Head Driver setup.')

        if self.next_step_idx:
            NextStepInvoker().invoke(
                self.next_step_idx, 
                self.invoker_type, 
                high_level_step_name=self.high_level_step_name,
                game_type=self.game_type,
            )
        return {'FINISHED'}

    def set_contraint_target_and_bone(self, constraint, armature, bone_name):
        constraint.target = armature
        constraint.subtarget = bone_name

    def set_inverse(self, object):
        bpy.context.view_layer.objects.active = object
        bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner='OBJECT')


register, unregister = bpy.utils.register_classes_factory(GI_OT_SetUpHeadDriver)
