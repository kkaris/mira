from mira.metamodel import ControlledConversion, Concept, NaturalConversion
from mira.dkg.web_client import is_ontological_child

# Provide to tests that are not meant to test ontological refinements;
# returning False ensures that tests that check context refinements only
# pass when the context refinement is True
simple_refinement_func = lambda x, y: False


def test_templates_equal():
    infected = Concept(name="infected population", identifiers={"ido": "0000511"})
    susceptible = Concept(name="susceptible population", identifiers={"ido": "0000514"})
    c1 = ControlledConversion(
        subject=Concept(name="susceptible"),
        outcome=Concept(name="infected"),
        controller=Concept(name="infected"),
    )
    c1_gnd = ControlledConversion(
        subject=susceptible,
        outcome=infected,
        controller=infected,
    )
    c2 = ControlledConversion(
        subject=Concept(name="susceptible"),
        outcome=Concept(name="infected"),
        controller=Concept(name="infected"),
    )
    c1_gnd_ctx = c1_gnd.with_context(location="Stockholm")
    c2_ctx = c2.with_context(location="Stockholm")
    assert not c1.is_equal_to(c2, with_context=False)
    assert c1_gnd.is_equal_to(c1_gnd, with_context=False)
    assert c1_gnd.is_equal_to(c1_gnd_ctx, with_context=False)
    assert not c1_gnd.is_equal_to(c1_gnd_ctx, with_context=True)
    assert not c1.is_equal_to(c2_ctx, with_context=True)
    assert not c1.is_equal_to(c2_ctx, with_context=False)


def test_concepts_equal():
    c1 = Concept(name="infected population", identifiers={"ido": "0000511"})
    c1_w_ctx = c1.with_context(location="Berlin")
    c2 = Concept(name="infected population", identifiers={"ido": "0000511"})
    c2_w_ctx = c2.with_context(location="Stockholm")

    assert c1.is_equal_to(c2)
    assert not c1_w_ctx.is_equal_to(c2_w_ctx, with_context=True)
    assert c1_w_ctx.is_equal_to(c2_w_ctx, with_context=False)


def test_template_type_inequality_is_equal():
    infected = Concept(name="infected population", identifiers={"ido": "0000511"})
    susceptible = Concept(name="susceptible population", identifiers={"ido": "0000514"})
    immune = Concept(name="immune population", identifiers={"ido": "0000592"})
    c1 = ControlledConversion(
        subject=susceptible,
        outcome=infected,
        controller=infected,
    )
    n1 = NaturalConversion(subject=infected, outcome=immune)
    assert not c1.is_equal_to(n1)


def test_template_type_inequality_refinement():
    infected = Concept(name="infected population", identifiers={"ido": "0000511"})
    susceptible = Concept(name="susceptible population", identifiers={"ido": "0000514"})
    immune = Concept(name="immune population", identifiers={"ido": "0000592"})
    c1 = ControlledConversion(
        subject=susceptible,
        outcome=infected,
        controller=infected,
    )
    n1 = NaturalConversion(subject=infected, outcome=immune)

    assert not c1.refinement_of(n1, refinement_func=simple_refinement_func)
    assert not n1.refinement_of(c1, refinement_func=simple_refinement_func)


def test_class_incompatibility_is_equal():
    infected = Concept(name="infected population", identifiers={"ido": "0000511"})
    immune = Concept(name="immune population", identifiers={"ido": "0000592"})
    nc = NaturalConversion(subject=infected, outcome=immune)

    assert not infected.is_equal_to(nc)
    assert not nc.is_equal_to(infected)


def test_class_incompatibility_refinement():
    infected = Concept(name="infected population", identifiers={"ido": "0000511"})
    immune = Concept(name="immune population", identifiers={"ido": "0000592"})
    natural_conversion = NaturalConversion(subject=infected, outcome=immune)

    assert not infected.refinement_of(natural_conversion, refinement_func=simple_refinement_func)
    assert not natural_conversion.refinement_of(infected, refinement_func=simple_refinement_func)
    assert not natural_conversion.is_equal_to(infected)


def test_template_context_refinement():
    infected = Concept(name="infected population", identifiers={"ido": "0000511"})
    immune = Concept(name="immune population", identifiers={"ido": "0000592"})
    natural_conversion = NaturalConversion(subject=infected, outcome=immune)
    nc_context = natural_conversion.with_context(location="Boston")
    # Test context refinement
    assert nc_context.refinement_of(
        natural_conversion, refinement_func=simple_refinement_func, with_context=True
    )


# Concepts refinement tests
def test_concept_refinement_grounding():
    # spatial region
    spatial_region = Concept(name="spatial region")
    spatial_region_gnd = Concept(name="spatial region", identifiers={"bfo": "0000006"})
    # one-dimensional spatial region
    one_dim_spat = Concept(name="one-dimensional spatial region")
    one_dim_spat_gnd = Concept(
        name="one-dimensional spatial region", identifiers={"bfo": "0000026"}
    )
    one_dim_spat_gnd_ctx = one_dim_spat_gnd.with_context(location="Stockholm")
    # test grounded
    assert one_dim_spat_gnd.refinement_of(
        spatial_region_gnd, refinement_func=is_ontological_child, with_context=False
    )
    assert not one_dim_spat_gnd.refinement_of(
        spatial_region, refinement_func=is_ontological_child, with_context=False
    )
    assert one_dim_spat_gnd.refinement_of(
        spatial_region_gnd, refinement_func=is_ontological_child, with_context=True
    )
    assert not one_dim_spat_gnd.refinement_of(
        spatial_region, refinement_func=is_ontological_child, with_context=True
    )
    assert one_dim_spat_gnd_ctx.refinement_of(
        one_dim_spat_gnd, refinement_func=is_ontological_child, with_context=True
    )

    # test ungrounded
    assert not spatial_region.refinement_of(
        one_dim_spat, refinement_func=is_ontological_child, with_context=False
    )
    spatial_region_ctx = spatial_region.with_context(location="Stockholm")
    # This one would be True if we consider names when ungrounded. Currently
    # ungrounded are not considered equal by definition.
    assert not spatial_region_ctx.refinement_of(
        spatial_region, refinement_func=is_ontological_child, with_context=True
    )
    #
    assert not spatial_region_ctx.refinement_of(
        spatial_region_gnd, refinement_func=is_ontological_child, with_context=True
    )


def test_concept_refinement_simple_context():
    spatial_region_gnd = Concept(name="spatial region", identifiers={"bfo": "0000006"})
    spatial_region_ctx = spatial_region_gnd.with_context(location="Stockholm")
    assert len(spatial_region_ctx.context)
    kw = {"refinement_func": is_ontological_child, "with_context": True}

    # Test both empty
    assert not spatial_region_gnd.refinement_of(spatial_region_gnd, **kw)

    # Test refined has context, other does not
    assert spatial_region_ctx.refinement_of(spatial_region_gnd, **kw)

    # Test other has context, refined does not
    assert not spatial_region_gnd.refinement_of(spatial_region_ctx, **kw)


def test_concept_refinement_context():
    spatial_region_gnd = Concept(name="spatial region", identifiers={"bfo": "0000006"})
    spatial_region_ctx = spatial_region_gnd.with_context(location="Stockholm")
    spatial_region_more_ctx = spatial_region_gnd.with_context(location="Stockholm", year=2010)
    spatial_region_diff_ctx = spatial_region_gnd.with_context(year=2007, count=10)

    kw = {"refinement_func": is_ontological_child, "with_context": True}

    # Exactly equal context
    assert not spatial_region_ctx.refinement_of(spatial_region_ctx, **kw)

    # Refined is subset of other
    assert not spatial_region_ctx.refinement_of(spatial_region_more_ctx, **kw)

    # Different contexts
    assert not spatial_region_more_ctx.refinement_of(spatial_region_diff_ctx, **kw)

    # Other is subset of refined
    assert spatial_region_more_ctx.refinement_of(spatial_region_ctx, **kw)


def test_provide_refinement_func():
    spatial_region_gnd = Concept(name="spatial region", identifiers={"bfo": "0000006"})
    two_dim_region_gnd = Concept(
        name="two-dimensional spatial region", identifiers={"bfo": "0000009"}
    )

    # This random function only check bfo grounded entities and the
    # identifier numbers, which is probably not a good idea in a real use case
    def refiner_func(child: str, parent: str) -> bool:
        if child.startswith("bfo") and parent.startswith("bfo"):
            child_id = int(child.split(":")[1])
            parent_id = int(parent.split(":")[1])
            return child_id > parent_id

        return False

    assert two_dim_region_gnd.refinement_of(spatial_region_gnd, refinement_func=refiner_func)
