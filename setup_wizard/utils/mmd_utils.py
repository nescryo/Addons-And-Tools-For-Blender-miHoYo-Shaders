# Author: Ivy (mmdsetup fork)
import os
import pathlib
import bpy


MMD_EXTENSIONS = {'.pmx', '.pmd'}

HEAD_BONE_CANDIDATES = [
    '頭',
    'Head',
    'head',
    'Bip001 Head',
    'bip_head',
    'mixamorig:Head',
    'Bone_Head',
    '頭_Head'
]

# Keywords for classifying MMD materials (Japanese, Chinese, English)
MMD_MATERIAL_KEYWORDS = {
    'Face': [
        '顔', 'フェイス', '目', '瞳', '眉', '口', '白目', 'まつげ', 'ハイライト',
        '脸', '表情', '眼睛', '眼白', '眉毛', '嘴', '睫毛',
        'face', 'head', 'eye', 'eyebrow', 'eyelash', 'mouth', 'pupil', 'brow'
    ],
    'Hair': [
        '髪', 'ヘアー', '前髪', '後髪', 'ツインテール', 'アホ毛', 'ポニーテール',
        '头发', '发', '刘海', '后发',
        'hair', 'twintail', 'ponytail', 'bangs'
    ],
    'Body_Trans': [
        '透', '半透明', '透明',
        'trans', 'alpha', 'glass'
    ],
    'Weapon': [
        '武器', '剣', '槍', '銃', '弓', '杖',
        'weapon', 'sword', 'gun', 'bow', 'spear', 'staff', 'blade'
    ],
    'Body': [
        '体', '身体', '身', '肌', '服', '衣装', '衣服', 'スカート', 'シャツ',
        'パンツ', '靴', '手', '腕', '足', '脚', '手袋', 'タイツ', 'ボディ',
        'body', 'skin', 'cloth', 'clothes', 'dress', 'skirt', 'shirt',
        'pants', 'shoe', 'shoes', 'arm', 'leg', 'sock', 'glove', 'outfit'
    ]
}


def is_mmd_filepath(filepath: str) -> bool:
    """Checks if filepath points to an MMD model (.pmx or .pmd)."""
    if not filepath:
        return False
    return pathlib.Path(filepath).suffix.lower() in MMD_EXTENSIONS


def is_mmd_object(obj) -> bool:
    """Checks if a Blender object is part of an MMD model structure created by mmd_tools."""
    if obj is None:
        return False
    
    # Direct mmd_type attribute provided by mmd_tools
    if hasattr(obj, 'mmd_type') and getattr(obj, 'mmd_type', 'NONE') != 'NONE':
        return True
    
    # Custom property or tag
    if 'mmd_type' in obj or 'mmd_root' in obj:
        return True
        
    # Check parent hierarchy for MMD root
    parent = getattr(obj, 'parent', None)
    while parent:
        if hasattr(parent, 'mmd_type') and getattr(parent, 'mmd_type', 'NONE') != 'NONE':
            return True
        if 'mmd_type' in parent or 'mmd_root' in parent:
            return True
        parent = getattr(parent, 'parent', None)

    return False


def find_head_bone_name(armature_bones) -> str:
    """
    Finds the head bone name in an armature.
    Supports MMD (Japanese '頭'), English ('Head'), and Unity/Bip bone conventions.
    """
    if not armature_bones:
        return ''

    # 1. Exact candidate match
    for candidate in HEAD_BONE_CANDIDATES:
        if candidate in armature_bones:
            return candidate

    # 2. Case-insensitive substring match
    bone_keys = list(armature_bones.keys())
    for bone_name in bone_keys:
        lower_name = bone_name.lower()
        if '頭' in bone_name or 'head' in lower_name:
            # Exclude neck/jaw bones if possible
            if 'neck' not in lower_name and 'jaw' not in lower_name:
                return bone_name

    return ''


def match_mmd_body_part_name(material_name: str) -> str:
    """
    Matches an MMD material name against known body parts.
    Returns canonical part name ('Face', 'Hair', 'Body', 'Body_Trans', 'Weapon') or None.
    """
    if not material_name:
        return None

    lower_mat = material_name.lower()

    # Prioritize Face and Hair first (since 'body' might match broadly)
    for category in ['Face', 'Hair', 'Body_Trans', 'Weapon', 'Body']:
        keywords = MMD_MATERIAL_KEYWORDS[category]
        for kw in keywords:
            if kw in material_name or kw in lower_mat:
                return category

    return None
