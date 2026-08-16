# SPDX-FileCopyrightText: 2026 Alexandr Savca
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import bootstrap
from .model import BuildContext


def _positive(value: str) -> int:
    parsed = int(value, 10)
    if parsed <= 0:
        raise argparse.ArgumentTypeError('must be positive')
    return parsed


def _nonnegative(value: str) -> int:
    parsed = int(value, 10)
    if parsed < 0:
        raise argparse.ArgumentTypeError('must be non-negative')
    return parsed


def parser(context: BuildContext) -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog='zlsystem',
        description='Construct Zeppe-Lin system products from explicit package authorities.',
    )
    result.add_argument('--version', action='version', version='zeppe-lin-system 0.1.0')
    products = result.add_subparsers(dest='product', required=True)

    bootstrap_parser = products.add_parser(
        'bootstrap', help='qualify a historical seed and construct the native runtime cohort')
    bootstrap_parser.add_argument(
        'action', nargs='?', default='run', choices=('run', 'resume', 'check', 'clean'),
        help='product action (default: run)')
    bootstrap_parser.add_argument(
        '--workspace', type=Path,
        default=context.build_root / 'products' / 'bootstrap',
        help='private bootstrap product workspace')
    bootstrap_parser.add_argument(
        '--seed', dest='seed_name',
        help='committed seed descriptor name; defaults to seeds/default')
    bootstrap_parser.add_argument(
        '--seed-file', type=Path,
        help='use these local archive bytes instead of downloading the selected seed')
    bootstrap_parser.add_argument(
        '--seed-signature-file', type=Path,
        help='use these local detached-signature bytes with --seed-file')
    bootstrap_parser.add_argument(
        '--foundation-source', type=Path,
        help='use an exact clean local pkgsrc-foundation checkout instead of cloning')
    bootstrap_parser.add_argument('--jobs', type=_positive, help='admitted build parallelism')
    bootstrap_parser.add_argument(
        '--source-date-epoch', type=_nonnegative,
        help='admitted reproducible build epoch')
    bootstrap_parser.add_argument(
        '--max-steps', type=_positive, default=8,
        help='live per-invocation transaction step budget (default: 8)')
    bootstrap_parser.add_argument(
        '--privilege', metavar='PROGRAM',
        help='execute native controller commands through PROGRAM, for example sudo')
    return result


def main(context: BuildContext) -> int:
    arguments = parser(context).parse_args()
    try:
        if arguments.product == 'bootstrap':
            options = bootstrap.BootstrapOptions(
                workspace=arguments.workspace,
                seed_name=arguments.seed_name,
                seed_file=arguments.seed_file,
                seed_signature_file=arguments.seed_signature_file,
                foundation_source=arguments.foundation_source,
                jobs=arguments.jobs,
                source_date_epoch=arguments.source_date_epoch,
                maximum_steps=arguments.max_steps,
                privilege=arguments.privilege,
            )
            if arguments.action == 'run':
                bootstrap.run(context, options)
            elif arguments.action == 'resume':
                bootstrap.resume(context, options)
            elif arguments.action == 'check':
                bootstrap.check(context, options)
            elif arguments.action == 'clean':
                bootstrap.clean(context, options)
            else:  # pragma: no cover - argparse closes the vocabulary.
                raise AssertionError(arguments.action)
        return 0
    except (bootstrap.BootstrapError, OSError, ValueError) as error:
        print(f'zlsystem: {error}', file=sys.stderr)
        return 1
