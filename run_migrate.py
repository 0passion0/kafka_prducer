import argparse
import sys

from application.migrate.info_to_nfsc import InfoToNsfc
from application.migrate.nfsc_to_es import NsfcToEs
from application.utils.decorators import log_execution, monitor_performance


@log_execution
@monitor_performance
def full_sync(task):
    match task:
        case "info_to_nsfc":  # 资源胡源数据同步到国自然基金资讯
            producer = InfoToNsfc()
            producer.sync()
        case "nsfc_to_es":  # 国自然基金资讯数据同步到ElasticSearch
            producer = NsfcToEs()
            producer.sync()
        case _:
            raise ValueError(f'无任务：{task}')


def main():
    sys.argv.extend([
        '--task', 'info_to_nsfc'
    ])
    parser = argparse.ArgumentParser(description='数据迁移工具')
    parser.add_argument('--task', required=True, help='迁移任务名')

    args = parser.parse_args()

    # 执行同步
    full_sync(args.task)


if __name__ == "__main__":
    "--task nfsc_task"
    main()
