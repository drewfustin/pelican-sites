import re
import warnings
import pandas as pd
import numpy as np
from string import Formatter
from psycopg2 import sql
from airflow.hooks.postgres_hook import PostgresHook
from drawbridge.connections.airflow import AirflowConnectionHandler
from drawbridge.util._decorators import cache_dataset
from drawbridge import queries

INITIAL_DATA_DATE = '2017-12-09'
DATASET_TO_VERSION_TABLE_TRANSLATION = {
    'properties': 'property_versions',
    'users': 'user_versions',
    'policies': 'policy_versions',
    'insureds': 'insured_versions',
    'people': 'people_versions'
}
DATASET_TO_ID_TRANSLATION = {
    'properties': 'property_id',
    'policies': 'policy_id',
    'people': 'person_id',
    'users': 'user_id',
    'insureds': 'insured_id',
    'addresses': 'address_id',
    'households': 'household_id'
}


class Inquisition(object):

    def __init__(self,
                 conn_id,
                 conn_cfg_path=None,
                 cache_path=None,
                 cache=False,
                 show_warnings=False):
        if not AirflowConnectionHandler().has_connection(conn_id) and conn_cfg_path:
            AirflowConnectionHandler().add_connection_from_file(conn_id, conn_cfg_path)

        self.conn = PostgresHook(postgres_conn_id=conn_id).get_conn()
        self.cache = cache
        self.cache_path = cache_path
        self.show_warnings = show_warnings

    @cache_dataset
    def query(self, inquiry, params=dict(), cache_name=None, cache=None):
        if cache is None:
            cache = self.cache
        if isinstance(inquiry, str):
            inquiry = Inquiry(query=inquiry, show_warnings=self.show_warnings)

        inquiry.fill_inquiry(self.conn, params)
        statement = inquiry.format_inquiry()

        return pd.read_sql_query(sql=statement, con=self.conn)

    @cache_dataset
    def get_table_snapshot(self, table_name, params=dict(), cache_name=None, cache=None):
        if cache is None:
            cache = self.cache

        inquiry = Inquiry(
            query='table_history',
            params=dict(
                table_name=DATASET_TO_VERSION_TABLE_TRANSLATION[table_name],
                date_max=params['date_max']
            ),
            subqueries=dict(
                selected_items=Inquiry(
                    query=table_name + '__selected',
                    params=params,
                    show_warnings=self.show_warnings
                )
            )
        )
        change_log = self.query(inquiry=inquiry)
        table_objects = (
            change_log.loc[pd.notnull(change_log['object_changes']), 'object']
            .apply(pd.Series))
        object_changes = (
            change_log.loc[pd.notnull(change_log['object_changes']), 'object_changes']
            .apply(lambda x: pd.Series(x).apply(pd.Series)[1].fillna('NONE_REPLACEMENT')))
        table_objects.update(object_changes)

        return table_objects.replace('NONE_REPLACEMENT', np.nan)

    @cache_dataset
    def get_dataset(self, dataset_name, params=dict(), cache_name=None, cache=None):
        data = self.query(dataset_name + '__selected', params)
        if dataset_name in DATASET_TO_VERSION_TABLE_TRANSLATION:
            data = data.merge(
                self.get_table_snapshot(dataset_name, params, cache=cache),
                how='left', on='id', suffixes=('', '__historical')
            )
        if dataset_name + '__combined' in queries.list_queries():
            data = data.merge(
                self.query(dataset_name + '__combined', params, cache=cache),
                how='left', left_on='id', right_on=DATASET_TO_ID_TRANSLATION[dataset_name],
                suffixes=('__historical', '__combined')
            )
        return data


class Inquiry(object):

    def __init__(self, query=None, params=dict(), subqueries=dict(), show_warnings=False):
        try:
            self.template = queries.get_sql(query)
        except (FileNotFoundError, OSError) as err:
            if show_warnings:
                warnings.warn("\n" + err.__str__() + "\nUsing supplied query as raw SQL.",
                              UserWarning)
            self.template = sql.SQL(re.sub('\s+', ' ', query).strip())
        self.show_warnings = show_warnings
        self.params = params or dict()
        self.subqueries = subqueries or dict()

    def format_inquiry(self):
        _placeholders = dict()

        for subquery_name, subquery in self.subqueries.items():
            _placeholders[subquery_name] = subquery.format_inquiry()

        for param_name, param_value in self.params.items():
            _placeholders[param_name] = sql.SQL(param_value)

        return self.template.format(**_placeholders)

    def fill_inquiry(self, conn, params=dict()):
        inquiry_keys = set([(i[0][-1] == '(', i[1])
                            for i in Formatter().parse(self.template.as_string(conn))
                            if i[1] is not None])
        for is_subquery, name in inquiry_keys:
            if is_subquery:
                if name not in self.subqueries:
                    self.subqueries[name] = Inquiry(name, show_warnings=self.show_warnings)
                self.subqueries[name].fill_inquiry(conn, params)
            else:
                if name not in self.params:
                    self.params[name] = params[name]
