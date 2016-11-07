# -*- coding: utf-8 -*-
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import os
import shutil
import logging
from anybox.recipe.odoo.server import ServerRecipe
from zc.buildout import UserError

logger = logging.getLogger(__name__)


class ReleaseRecipe(ServerRecipe):
    """Recipe to build a self-contained and offline playable archive
    """

    def __init__(self, *a, **kw):
        super(ReleaseRecipe, self).__init__(*a, **kw)
        self.offline = True
        opt = self.options
        opt.pop('freeze-to', None)
        opt.pop('extract-downloads-to', None)
        self.release_dir = opt.setdefault('release-dir', 'release')
        clean_dir = opt.setdefault('clean-dir', 'false').lower()
        self.clean_release_dir = clean_dir == 'true'
        if os.path.exists(self.release_dir):
            if self.clean_release_dir:
                logger.info("Clean release directory %s", self.release_dir)
                shutil.rmtree(self.release_dir)
                return
            raise UserError('Target dir \'%s\' already exists. '
                            'Delete-it before running or set \'clean-dir\' '
                            'option to true in your config.'
                            '' % self.release_dir)

    def install(self):
        self.merge_requirements()
        self.install_requirements()
        self.extract_downloads_to(self.release_dir)
        return self.openerp_installed

    update = install

    def _extract_sources(self, out_conf, target_dir, extracted):
        # since our recipe is an extension used to build the release package
        # we need to put the right recipe to use to install the server from
        # the generated configuration
        recipe = self.options.get('recipe', 'anybox.recipe.odoo:server')
        recipe = recipe.replace(':release', ':server')
        self.options['recipe'] = recipe
        vals = super(ReleaseRecipe, self)._extract_sources(
            out_conf, target_dir, extracted)
        return vals

    def _prepare_extracted_buildout(self, conf, target_dir):
        super(ReleaseRecipe, self)._prepare_extracted_buildout(conf, target_dir)
        # remove the extends directive from buildout section if specified
        # In some case it's usefull to generated a configuration file without 
        # dependencies on other other files
        no_extends = self.options.setdefault(
            'no-extends', 'false')
        if no_extends.lower() == 'true':
             conf.set('buildout', 'extends', '')

