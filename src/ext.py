def delete_lump(src: str, before: list[str]):
    for b in before:
        src.replace(b, '')
    return src
