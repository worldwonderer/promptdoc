import pytest

from tests.helpers import auth_headers


@pytest.mark.unit
def test_locale_endpoint_sets_cookie(client):
    response = client.get('/locale/zh_Hans')
    assert response.status_code == 302
    set_cookie = response.headers.get('Set-Cookie', '')
    assert 'locale=zh_Hans' in set_cookie


@pytest.mark.unit
def test_locale_endpoint_redirects_back(client):
    response = client.get('/locale/zh_Hans', headers={'Referer': 'http://localhost/admin/prompts'})
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/admin/prompts'


@pytest.mark.unit
def test_locale_endpoint_invalid_returns_404(client):
    response = client.get('/locale/fr')
    assert response.status_code == 404


@pytest.mark.unit
def test_locale_endpoint_rejects_external_referrer(client):
    response = client.get('/locale/zh_Hans', headers={'Referer': 'https://evil.com/phishing'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/'


@pytest.mark.unit
def test_login_page_renders_chinese_with_cookie(client):
    client.set_cookie('locale', 'zh_Hans')
    response = client.get('/admin/login')
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert '欢迎回来' in page
    assert 'Welcome Back' not in page


@pytest.mark.unit
def test_login_page_renders_english_by_default(client):
    response = client.get('/admin/login')
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert 'Welcome Back' in page


@pytest.mark.unit
def test_html_lang_attribute_reflects_locale(client):
    client.set_cookie('locale', 'zh_Hans')
    response = client.get('/admin/login')
    page = response.get_data(as_text=True)
    assert 'lang="zh_Hans"' in page


@pytest.mark.unit
def test_html_lang_attribute_default_en(client):
    response = client.get('/admin/login')
    page = response.get_data(as_text=True)
    assert 'lang="en"' in page


@pytest.mark.unit
def test_api_unauthorized_stays_english_regardless_of_locale(client):
    client.set_cookie('locale', 'zh_Hans')
    response = client.get('/api/prompts')
    assert response.status_code == 401
    assert response.json == {'error': 'Unauthorized'}
