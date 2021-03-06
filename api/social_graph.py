import networkx as nx
from api.models import Person, Photo
import itertools
from django.db.models import Count
from django.db.models import Q

def build_social_graph(user):
    G = nx.Graph()

    people = list(Person.objects.filter(Q(faces__photo__hidden=False) & Q(faces__photo__owner=user)).distinct().annotate(face_count=Count('faces')).filter(Q(face_count__gt=0)).order_by('-face_count'))[1:]
    for person in people:
        person = Person.objects.prefetch_related('faces__photo__faces__person').filter(id=person.id)[0]
        for this_person_face in person.faces.all():
            for other_person_face in this_person_face.photo.faces.all():
                G.add_edge(person.name,other_person_face.person.name)
    pos = nx.spring_layout(G,scale=1000,iterations=20)
    nodes = [{'id':node,'x':pos[0],'y':pos[1]} for node,pos in pos.items()]
    links = [{'source':pair[0], 'target':pair[1]} for pair in G.edges()]
    res = {"nodes":nodes, "links":links}
    return res

def build_ego_graph(person_id):
    G = nx.Graph()
    person = Person.objects.prefetch_related('faces__photo__faces__person').filter(id=person_id)[0]
    for this_person_face in person.faces.all():
        for other_person_face in this_person_face.photo.faces.all():
            G.add_edge(person.name,other_person_face.person.name)
    nodes = [{'id':node} for node in G.nodes()]
    links = [{'source':pair[0], 'target':pair[1]} for pair in G.edges()]
    res = {"nodes":nodes, "links":links}
    return res
