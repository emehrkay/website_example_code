import asyncio
from gizmo import Request, Vertex, Edge, Mapper, String
from gremlinpy import Gremlin

# setup the connection
request = Request('localhost', 8182)
gremlin = Gremlin('blog')
mapper = Mapper(request=request, gremlin=gremlin)


class BaseBlogEntity(object):

    @property
    def data(self):
        data = super().data
        fixed = {}

        for field, value in data.items():
            if (isinstance(value, list) and len(value)
                and isinstance(value[-1], dict)
                and 'value' in value[-1]):
                fixed[field] = value[-1]['value']
            else:
                fixed[field] = value

        return fixed


class BaseBlogMapper(object):
    async def data(self, entity):
        fixed = {}
        data = await super(BaseMapper, self).data(entity=entity)

        if not entity:
            return fixed

        for field, value in data.items():
            if (isinstance(value, list) and len(value)
                and isinstance(value[-1], dict)
                and 'value' in value[-1]):
                fixed[field] = value[-1]['value']
            else:
                fixed[field] = value

        return fixed


from gizmo.entity import Vertex, Edge
from gizmo.field import String, Boolean, DateTime


class User(BaseBlogEntity, Vertex):
    name = String()


class Post(BaseBlogEntity, Vertex):
    title = String()
    slug = String()
    content = String()
    published = Boolean(values=False)
    date = DateTime()


class Tag(BaseBlogEntity, Vertex):
    tag = String()


class Author(BaseBlogEntity, Edge):
    pass


class HasTag(BaseBlogEntity, Edge):
    pass


from gizmo.mapper import EntityMapper


class HasAuthorMapper(BaseBlogMapper, EntityMapper):
    entity = Author
    unique = 'both'


class UserMapper(BaseBlogMapper, EntityMapper):
    entity = User
    unique = ('name')


class PostMapper(BaseBlogMapper, EntityMapper):
    entity = Post
    unique = ('slug')


class TagMapper(BaseBlogMapper, EntityMapper):
    entity = Tag
    unique = ('tag')
