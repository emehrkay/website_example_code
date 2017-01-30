import asyncio

from tornado.web import Application, HTTPError, RequestHandler
from tornado import httpserver, platform

from gremlinpy import Param

from model import mapper, Post, User, Author


UUID_RE = '[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
PORT = 9997
USER_ID = 'f91046f0-9b25-4c85-bf10-66dd6acd8470'


class BlogHandler(RequestHandler):

    async def get_by_id(self, id):
        try:
            if not id:
                raise

            _id = Param('GET_BY_ID', id)
            g = mapper.gremlin.V().hasId(_id)
            res = await mapper.query(gremlin=g)
            entity = res.first()

            if not entity:
                raise

            return entity
        except Exception as e:
            raise HTTPError(404)

    @property
    def data(self):
        return {
            'title': self.get_argument('title'),
            'content': self.get_argument('content'),
            'published': self.get_argument('published', False),
            'tags': self.get_arguments('tags'),
        }

    async def get(self, id):
        entry = await self.get_by_id(id)
        data = await mapper.data(entry)

        return self.write(data)

    async def post(self, id=None):
        # we'll create a new blog post and connect it to the user
        entry = mapper.create(self.data, entity=Post)
        user = await self.get_by_id(USER_ID)
        author = mapper.connect(user, entry, edge_entity=Author)
        await mapper.save(author).send()
        await mapper.add_tags(entry, self.data['tags'])
        import pudb; pu.db
        data = await mapper.data(entry)

        return self.write(data)

    async def put(self, id):
        entry = await self.get_by_id(id)
        entry.hydrate(self.data)
        await mapper.save(entry).send()
        await mapper.add_tags(entry, self.data['tags'])
        data = await mapper.data(entry)

        return self.write(data)

    async def delete(self, id):
        entry = await self.get_by_id(id)
        await mapper.delete(entry).send()

        return self.write('Blog {} deleted'.format(entry['title']))


class PostsHandler(RequestHandler):

    async def get(self):
        g = mapper.start(Post)
        res = await mapper.query(gremlin=g)
        data = {'data': res.mapper_data}

        return self.write(data)


def make_app():
    routes = [
        (r'/blog(?:/(' + UUID_RE + ')?)?/?', BlogHandler),
        (r'/posts/?', PostsHandler),
    ]
    settings = {
        'debug': True,
    }
    return Application(routes, **settings) 


if __name__ == "__main__":
    platform.asyncio.AsyncIOMainLoop().install()

    ioloop = asyncio.get_event_loop()
    app = make_app()
    server = httpserver.HTTPServer(app)
    server.listen(PORT)
    print('Server Running on Port: {}'.format(PORT))
    ioloop.run_forever()
