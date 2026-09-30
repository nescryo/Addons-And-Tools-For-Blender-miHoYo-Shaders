import unittest
from setup_wizard.utils.mmd_utils import (
    is_mmd_filepath,
    is_mmd_object,
    find_head_bone_name,
    match_mmd_body_part_name,
)


class MockObject:
    def __init__(self, name, mmd_type=None, parent=None, custom_props=None):
        self.name = name
        if mmd_type is not None:
            self.mmd_type = mmd_type
        self.parent = parent
        self._props = custom_props or {}

    def __contains__(self, key):
        return key in self._props

    def __getitem__(self, key):
        return self._props[key]


class TestMMDUtils(unittest.TestCase):
    def test_is_mmd_filepath(self):
        self.assertTrue(is_mmd_filepath("character.pmx"))
        self.assertTrue(is_mmd_filepath("model.PMX"))
        self.assertTrue(is_mmd_filepath("/path/to/char.pmd"))
        self.assertFalse(is_mmd_filepath("model.fbx"))
        self.assertFalse(is_mmd_filepath("model.blend"))
        self.assertFalse(is_mmd_filepath(""))

    def test_is_mmd_object(self):
        # Regular empty
        regular_empty = MockObject("Empty")
        self.assertFalse(is_mmd_object(regular_empty))

        # Direct MMD empty
        mmd_rigid = MockObject("mmd_rigid", mmd_type="RIGID_BODY")
        self.assertTrue(is_mmd_object(mmd_rigid))

        # None type MMD
        mmd_none = MockObject("non_mmd", mmd_type="NONE")
        self.assertFalse(is_mmd_object(mmd_none))

        # Child of MMD root
        mmd_root = MockObject("Model_Root", mmd_type="ROOT")
        child_joint = MockObject("Joint_Empty", parent=mmd_root)
        self.assertTrue(is_mmd_object(child_joint))

    def test_find_head_bone_name(self):
        # MMD Japanese name
        bones_jp = {"全ての親": None, "センター": None, "首": None, "頭": None}
        self.assertEqual(find_head_bone_name(bones_jp), "頭")

        # English standard
        bones_en = {"Root": None, "Hips": None, "Spine": None, "Neck": None, "Head": None}
        self.assertEqual(find_head_bone_name(bones_en), "Head")

        # Unity Bip name
        bones_bip = {"Bip001": None, "Bip001 Pelvis": None, "Bip001 Head": None}
        self.assertEqual(find_head_bone_name(bones_bip), "Bip001 Head")

        # Fallback substring
        bones_sub = {"Bone_head_01": None}
        self.assertEqual(find_head_bone_name(bones_sub), "Bone_head_01")

        # Empty or missing
        self.assertEqual(find_head_bone_name({}), "")

    def test_match_mmd_body_part_name(self):
        # Japanese
        self.assertEqual(match_mmd_body_part_name("顔"), "Face")
        self.assertEqual(match_mmd_body_part_name("髪"), "Hair")
        self.assertEqual(match_mmd_body_part_name("体"), "Body")
        self.assertEqual(match_mmd_body_part_name("服"), "Body")
        self.assertEqual(match_mmd_body_part_name("スカート"), "Body")
        self.assertEqual(match_mmd_body_part_name("半透明"), "Body_Trans")
        self.assertEqual(match_mmd_body_part_name("武器"), "Weapon")

        # Chinese
        self.assertEqual(match_mmd_body_part_name("脸"), "Face")
        self.assertEqual(match_mmd_body_part_name("头发"), "Hair")
        self.assertEqual(match_mmd_body_part_name("身体"), "Body")
        self.assertEqual(match_mmd_body_part_name("衣服"), "Body")
        self.assertEqual(match_mmd_body_part_name("透明"), "Body_Trans")

        # English
        self.assertEqual(match_mmd_body_part_name("Face_Material"), "Face")
        self.assertEqual(match_mmd_body_part_name("Hair_Front"), "Hair")
        self.assertEqual(match_mmd_body_part_name("Cloth_Dress"), "Body")
        self.assertEqual(match_mmd_body_part_name("Alpha_Glass"), "Body_Trans")


if __name__ == "__main__":
    unittest.main()
