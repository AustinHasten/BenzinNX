from collections import namedtuple

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
pat_tup = namedtuple('pat1', ['length', 'animorder', 'numseconds', 'firstoffset', 'secondsoffset', 'start', 'end', 'childbinding', 'pad', 'pad1'])
pai_tup = namedtuple('pai1', ['length', 'framesize', 'flags', 'pad', 'numtimgs', 'numentries', 'entryoffset'])
entry_tup = namedtuple('entry', ['num_tags', 'is_material', 'pad'])
tag_data_tup = namedtuple('tag_data', ['type1', 'type2', 'datatype', 'coordcount', 'pad1', 'offsettotagdata'])
