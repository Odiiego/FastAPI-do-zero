from http import HTTPStatus

import factory.fuzzy

from fast_zero.models import Todo, TodoState


def test_create_todo(client, token):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'state': 'draft',
        },
    )
    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
    }


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_list_todos_should_return_5_todos(session, client, user, token):
    excepted_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == excepted_todos


def test_list_todos_pagination(session, client, user, token):
    expected_todos = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_title(session, client, user, token):
    expected_todo = 1
    complete_todos = 5

    session.bulk_save_objects(
        TodoFactory.create_batch(4, user_id=user.id, title='Title')
    )
    session.add(
        TodoFactory.create(user_id=user.id, title='Test filter by title')
    )
    session.commit()

    response = client.get(
        '/todos/?title=Test filter by title',
        headers={'Authorization': f'Bearer {token}'},
    )
    completeResponse = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todo
    assert len(completeResponse.json()['todos']) == complete_todos


def test_list_todos_filter_description(session, client, user, token):
    expected_todo = 1
    complete_todos = 5

    session.bulk_save_objects(
        TodoFactory.create_batch(4, user_id=user.id, description='Description')
    )
    session.add(
        TodoFactory.create(
            user_id=user.id, description='Test filter by description'
        )
    )
    session.commit()

    response = client.get(
        '/todos/?description=Test filter by description',
        headers={'Authorization': f'Bearer {token}'},
    )
    completeResponse = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todo
    assert len(completeResponse.json()['todos']) == complete_todos


def test_list_todos_filter_state(session, client, user, token):
    expected_todo = 1
    complete_todos = 5

    session.bulk_save_objects(
        TodoFactory.create_batch(4, user_id=user.id, state=TodoState.draft)
    )
    session.add(TodoFactory.create(user_id=user.id, state=TodoState.todo))
    session.commit()

    response = client.get(
        '/todos/?state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )
    completeResponse = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todo
    assert len(completeResponse.json()['todos']) == complete_todos


def test_list_todos_filter_combined(session, client, user, token):
    expected_todo = 1
    complete_todos = 5

    session.bulk_save_objects(
        TodoFactory.create_batch(
            4,
            user_id=user.id,
            title='Title',
            description='Description',
            state=TodoState.draft,
        )
    )
    session.add(
        TodoFactory.create(
            user_id=user.id,
            title='Filter',
            description='Filter',
            state=TodoState.todo,
        )
    )
    session.commit()

    response = client.get(
        '/todos/?title=Filter&description=Filter&state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )
    completeResponse = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todo
    assert len(completeResponse.json()['todos']) == complete_todos


def test_patch_todo_error(client, token):
    response = client.patch(
        '/todos/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_patch_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id, title='Nome provisório')

    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_delete_todo(session, client, user, token):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


def test_delete_todo_error(client, token):
    response = client.delete(
        '/todos/10', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}
