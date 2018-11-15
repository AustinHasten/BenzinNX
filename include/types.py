from collections import namedtuple

wraps = ["NEAR_CLAMP", "NEAR_REPEAT", "NEAR_MIRROR", "GX2_MIRROR_ONCE", "CLAMP", "REPEAT", "MIRROR", "GX2_MIRROR_ONCE_BORDER" ]
originX = ["Center", "Left", "Right"]
originY = ["Center", "Up", "Down"]
MappingTypes = ["UVMapping", "", "", "OrthogonalProjection", "PaneBasedProjection"]
BlendTypes = ["Max", "Min"]
ColorBlendTypes = ["Overwrite", "Multiplicative", "Additive", "Exclusion", "4", "Subtractive", "ColorDodge", "ColorBurn", "Overlay", "Indirect", "BlendIndirect", "EachIndirect"]
AlphaTestCondition = ["Never", "Less", "LessEqual", "Equal", "NotEqual", "GreaterEqual", "Greater", "Always"]
BlendCalc = ["0", "1", "FBColor", "1-FBColor", "PixelAlpha", "1-PixelAlpha", "FBAlpha", "1-FBAlpha", "PixelColor", "1-PixelColor"]
BlendCalcOp = ["0", "Add", "Subtract", "ReverseSubtract", "Min", "Max"]
LogicalCalcOp = ["None", "NoOp", "Clear", "Set", "Copy", "InvCopy", "Inv", "And", "Nand", "Or", "Nor", "Xor", "Equiv", "RevAnd", "InvAnd", "RevOr", "InvOr"]
ProjectionMappingTypes = ["Standard", "EntireLayout", "2", "3", "PaneRandSProjection", "5", "6"]
TextAlign = ["NA", "Left", "Center", "Right"]

#anim types
typedict = {
    'FLPA': ["Xtrans", "Ytrans", "Ztrans", "Xrotate", "Yrotate", "Zrotate", "Xscale", "Yscale", "Xsize", "Ysize"],
    'FLVI': ["visible"],
    'FLTP': ["TexturePattern"],
    'FLVC': ["LT_red", "LT_green", "LT_blue", "LT_alpha", "RT_red", "RT_green", "RT_blue", "RT_alpha", "LB_red", "LB_green", "LB_blue", "LB_alpha", "RB_red", "RB_green", "RB_blue", "RB_alpha", "PaneAlpha"],
    'FLMC': ["BlackColor_red", "BlackColor_green", "BlackColor_blue", "BlackColor_alpha", "WhiteColor_red", "WhiteColor_green", "WhiteColor_blue", "WhiteColor_alpha"],
    'FLTS': ["Utrans", "Vtrans", "rotate", "Uscale", "Vscale"],
    'FLIM': ["rotate", "Uscale", "Vscale"]
}
bflanheader_tup = namedtuple('bflan', ['endian', 'firstsectionoffsetree', 'version', 'pad1', 'filesize', 'sections', 'pad2'])
pat1section_tup = namedtuple('pat1', ['length', 'animorder', 'numseconds', 'firstoffset', 'secondsoffset', 'start', 'end', 'childbinding', 'pad', 'pad1'])
pai1section_tup = namedtuple('pai1', ['length', 'framesize', 'flags', 'pad', 'numtimgs', 'numentries', 'entryoffset'])
entry_tup = namedtuple('entry', ['num_tags', 'is_material', 'pad'])
tag_data_tup = namedtuple('offset', ['type1', 'type2', 'datatype', 'coordcount', 'pad1', 'offsettotagdata'])
