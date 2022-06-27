import logging
from uuid import UUID

server_offset_map = {
    'write': 1,
    'read': 2,
}

def compare_node(uuid1: str, uuid2: str) -> bool:
    return UUID(uuid1).node == UUID(uuid2).node

def check_fill_empty(service_uuid: str, uuid: str, typ: str) -> str:
    if not uuid:
        uuid = derive_chars_from_service(service_uuid, server_offset_map[typ])
        logging.warning(f'No {typ} uuid specified, derived from service {service_uuid} -> {uuid}')

    assert compare_node(service_uuid, uuid), f'Service and {typ} uuid are not from the same family'

    return uuid

def derive_chars_from_service(service_uuid: str, offset: int) -> str:
    uid = UUID(service_uuid)
    field_list = list(uid.fields)
    field_list[0] += offset
    return str(UUID(fields=field_list))