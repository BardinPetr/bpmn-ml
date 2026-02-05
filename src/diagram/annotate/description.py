import numpy as np

from src.diagram.description_models import GBPMNElementType, GBPMNFlowType


def print_story(story):
    text = ''
    for type, label in [[i.type, i.label] for i in story]:
        if label is None:
            if type != GBPMNFlowType.SEQUENCE:
                text += type.value + ' '
            elif type == GBPMNFlowType.MESSAGE:
                text += '-(msg)->'
            continue
        if isinstance(type, GBPMNFlowType):
            if type == GBPMNFlowType.SEQUENCE:
                pass
                # print('-->', end=' ')
        else:
            text += f"**{type}**(_{label}_) "
    return text


def make_description(contents):
    text = ""
    story_list = list()
    visited_idx = set()

    EXCPET_SET = {GBPMNElementType.VIRT_LANE, GBPMNElementType.VIRT_PROC}

    all_id_set = set([i.id for i in contents.elements if i.type not in EXCPET_SET])

    def get_neighbors_idx(id):
        neighbors_ids_list = dict()
        for line in contents.links:
            if line.source_id == id:
                neighbors_ids_list[line.target_id] = line.id
        return neighbors_ids_list  # "{el_id: link_id}"

    def find_el(id):
        return [i for i in contents.elements if i.id == id][0]

    def find_link(id):
        return [i for i in contents.links if i.id == id][0]

    def dfs(id, cur_story=list()):
        nonlocal visited_idx
        if id in visited_idx: return
        visited_idx.add(id)
        el = find_el(id)
        cur_story.append(el)

        if id in all_id_set:
            all_id_set.remove(id)

        neighbors_idx = get_neighbors_idx(id).items()
        if len(neighbors_idx) == 0:
            story_list.append(cur_story)
        for neighbor_id, line_id in neighbors_idx:
            line = find_link(line_id)
            cur_story.append(line)
            dfs(neighbor_id, cur_story.copy())

    event_start_list_id = [
        i.id for i in contents.elements if i.type == GBPMNElementType.EVENT_START
    ]

    for id in event_start_list_id:
        dfs(id)

    while len(set(all_id_set)) > 0:
        all_id_list = list(all_id_set)
        next_id = np.argmin([np.sqrt(find_el(i).bbox[0] ** 2 + find_el(i).bbox[1] ** 2) for i in all_id_list])
        visited_idx = set()
        dfs(all_id_list[next_id])

    for story in story_list:
        text += print_story(story) + '\n\n'

    return text
