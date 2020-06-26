from repoze.what.adapters import BaseSourceAdapter

class DocuGroupSourceAdapter(BaseSourceAdapter):
    """Docu group source adapter"""

    def _get_all_sections(self):
        return Group.objects(db)

    def _get_section_items(self, section):
        return Member.objects(db).where(groups__contains=section)

    def _find_sections(self, credentials):
        userid = credentials['repoze.what.userid']
        return Member.object(db, userid)

    def _include_items(self, section, items):
        for item in items:
            if not section in item.groups:
                item.groups.append(section)
                item.save()

    def _exclude_items(self, section, items):
        for item in items:
            item.groups.pop(section)
            item.save()

    def _item_is_included(self, section, item):
        return item in self.get_section_items(section)

    def _create_section(self, section):
        self.fake_sections[section] = set()

    def _edit_section(self, section, new_section):
        self.fake_sections[new_section] = self.fake_sections[section]
        del self.fake_sections[section]

    def _delete_section(self, section):
        Group.objects(db, section).delete()

    def _section_exists(self, section):
        section in Group.objects(db)


class FakeGroupSourceAdapter(BaseSourceAdapter):
    """Mock group source adapter"""

    def __init__(self, *args, **kwargs):
        super(FakeGroupSourceAdapter, self).__init__(*args, **kwargs)
        self.fake_sections = {
            u'admins': set([u'andy', u'rms']),
            u'developers': set([u'rms', u'linus']),
            u'trolls': set([u'sballmer']),
            u'python': set(),
            u'php': set()
            }

    def _get_all_sections(self):
        return self.fake_sections

    def _get_section_items(self, section):
        return self.fake_sections[section]

    def _find_sections(self, credentials):
        username = credentials['repoze.what.userid']
        return set([n for (n, g) in self.fake_sections.items()
                    if username in g])

    def _include_items(self, section, items):
        self.fake_sections[section] |= items

    def _exclude_items(self, section, items):
        for item in items:
            self.fake_sections[section].remove(item)

    def _item_is_included(self, section, item):
        return item in self.fake_sections[section]

    def _create_section(self, section):
        self.fake_sections[section] = set()

    def _edit_section(self, section, new_section):
        self.fake_sections[new_section] = self.fake_sections[section]
        del self.fake_sections[section]

    def _delete_section(self, section):
        del self.fake_sections[section]

    def _section_exists(self, section):
        return self.fake_sections.has_key(section)

class FakePermissionSourceAdapter(BaseSourceAdapter):
    """Mock permissions source adapter"""

    def __init__(self, *args, **kwargs):
        super(FakePermissionSourceAdapter, self).__init__(*args, **kwargs)
        self.fake_sections = {
            u'see-site': set([u'trolls']),
            u'edit-site': set([u'admins', u'developers']),
            u'commit': set([u'developers'])
            }

    def _get_all_sections(self):
        return self.fake_sections

    def _get_section_items(self, section):
        return self.fake_sections[section]

    def _find_sections(self, group_name):
        return set([n for (n, p) in self.fake_sections.items()
                    if group_name in p])

    def _include_items(self, section, items):
        self.fake_sections[section] |= items

    def _exclude_items(self, section, items):
        for item in items:
            self.fake_sections[section].remove(item)

    def _item_is_included(self, section, item):
        return item in self.fake_sections[section]

    def _create_section(self, section):
        self.fake_sections[section] = set()

    def _edit_section(self, section, new_section):
        self.fake_sections[new_section] = self.fake_sections[section]
        del self.fake_sections[section]

    def _delete_section(self, section):
        del self.fake_sections[section]

    def _section_exists(self, section):
        return self.fake_sections.has_key(section)
