import cProfile

from lagom import Container, Singleton, magic_bind_to_container

from scripts.timing.core_domain import SomeOtherThingAsAsingleton, SomeService, AThingIMightNeed

container = Container()
container[SomeOtherThingAsAsingleton] = Singleton(SomeOtherThingAsAsingleton)


@magic_bind_to_container(container, shared=[SomeService])
def do_work(thing: AThingIMightNeed):
    thing.do_it()


def run_test():
    for _ in range(1_600_00):
        do_work()


if __name__ == "__main__":
    cProfile.run("run_test()")

