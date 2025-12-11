from sqlalchemy import text


def test_fn_etl_data_load_cleans_and_transforms(engine):
    with engine.connect() as conn:
        conn.execute(text("truncate table s_sql_dds.t_sql_source_unstructured cascade"))
        conn.execute(text("truncate table s_sql_dds.t_sql_source_structured cascade"))

        conn.execute(text("""
            insert into s_sql_dds.t_sql_source_unstructured
                (id, name, country, city, age, gender, email, status, value, register_date)
            values
                ('1', '', 'russia', 'moscow', -5, 'male', 'bad_email', 'new', -10, '2023-01-01'),
                ('2', 'ivan', 'ru', '', 25, 'male', 'ivan@example.com', 'active', 100.5, '2024-06-01'),
                ('3', null, 'DE', 'berlin', 999, 'female', null, 'deleted', null, '2024-01-15');
        """))
        conn.commit()

        conn.execute(
            text("select s_sql_dds.fn_etl_data_load('2022-01-01', '2025-12-31')")
        )
        conn.commit()

        res = conn.execute(
            text("""
                select id, name, country, city, age, gender, email, status, value, register_date
                from s_sql_dds.t_sql_source_structured
                order by id
            """)
        ).fetchall()

    assert len(res) == 3

    r1 = res[0]
    assert r1.id == '1'
    assert r1.name == 'unknown'
    assert r1.country == 'unknown'
    assert r1.city == 'moscow'
    assert r1.age is None
    assert r1.gender == 'male'
    assert r1.email == 'unknown'
    assert r1.status == 'new'
    assert r1.value is None
    assert str(r1.register_date) == '2023-01-01'

    r2 = res[1]
    assert r2.id == '2'
    assert r2.name == 'ivan'
    assert r2.country == 'RU'
    assert r2.city == 'unknown'
    assert r2.age == 25
    assert r2.gender == 'male'
    assert r2.email == 'ivan@example.com'
    assert r2.status == 'active'
    assert float(r2.value) == 100.5
    assert str(r2.register_date) == '2024-06-01'

    r3 = res[2]
    assert r3.id == '3'
    assert r3.name == 'unknown'
    assert r3.country == 'DE'
    assert r3.city == 'berlin'
    assert r3.age is None
    assert r3.gender == 'female'
    assert r3.email == 'unknown'
    assert r3.status == 'deleted'
    assert r3.value is None
    assert str(r3.register_date) == '2024-01-15'
