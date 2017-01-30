import asyncio
from gizmo import Request, Vertex, Edge, Mapper, String
from gremlinpy import Gremlin, Param

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
        data = await super(BaseBlogMapper, self).data(entity=entity)

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


class HasTagMapper(BaseBlogMapper, EntityMapper):
    entity = HasTag
    unique = 'both'


class UserMapper(BaseBlogMapper, EntityMapper):
    entity = User
    unique = ('name',)


class PostMapper(BaseBlogMapper, EntityMapper):
    entity = Post
    unique_fields = ('slug',)

    async def data(self, entity):
        data = data = await super(PostMapper, self).data(entity=entity)
        tags = await self.get_tags(entity)
        data['Tags'] = await tags.mapper_data

        return data

    async def get_tags(self, entity):
        gremlin = self.mapper.start(entity)

        gremlin.func('out', Param('has_tag', 'has_tag'))

        res = await self.mapper.query(gremlin=gremlin)

        return res

    async def add_tags(self, entity, tags=None):
        tags = tags or []

        if not isinstance(tags, (list, set)):
            tags = [tags,]

        existing = await self.get_tags(entity)
        to_remove = [t for t in existing if t['tag'] not in tags]
        to_remove_name = [t['tag'] for t in to_remove]
        to_add = set(tags) - set(to_remove_name)

        for name in to_add:
            tag = self.mapper.create({'tag': name}, Tag)
            tag_edge = self.mapper.connect(entity, tag,
                edge_entity=HasTag)

            await self.mapper.save(tag_edge).send()

        # here we want to get the edge between the entity and
        # the tag to be removed and remove that
        for tag in to_remove:
            # dont put this heere in real code
            from gremlinpy.statement import GetEdge
            try:
                get_edge = GetEdge(entity['id'], tag['id'], 'has_tag',
                    'both')
                self.mapper.gremlin.apply_statement(get_edge)
                res = await self.mapper.query(gremlin=self.mapper.gremlin)
                has_tag = res.first()
                await self.mapper.delete(has_tag).send()
            except:
                pass


class TagMapper(BaseBlogMapper, EntityMapper):
    entity = Tag
    unique_fields = ('tag',)
