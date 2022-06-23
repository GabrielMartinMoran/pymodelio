from test.test_models.person import Person, PersonNestedModel

#pnm = PersonNestedModel(id=123456)
pnm = PersonNestedModel()

pnm_2 = PersonNestedModel(id=123456)

p = Person(dni=38829825, name='Gabriel', public_attr='Public attr', nested_model=pnm, nested_models=[pnm_2])
assert p.dni == 38829825
assert p.name == 'Gabriel'
assert p.public_attr == 'Public attr'
assert p.private_default_attr == 'Hi from private default!'
