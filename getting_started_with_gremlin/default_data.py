import asyncio

from model import mapper, User


async def default():
    user = mapper.create({'name': 'default user'}, entity=User)

    await mapper.save(user).send()

    print('Saved user with id: {}'.format(user['id']))


asyncio.get_event_loop().run_until_complete(default())
