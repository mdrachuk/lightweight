import os
import shutil
from pathlib import Path
from uuid import uuid4

import pytest

from lightweight.site import Site


class TestIncludeFile:

    def setup(self):
        self.file_path = Path('test.html')
        self.test_content = 'This is a test!'
        with self.file_path.open('w') as f:
            f.write(self.test_content)

    def teardown(self):
        os.remove(self.file_path)

    def test_include(self, tmp_path: Path):
        out_path = tmp_path / 'out'
        site = Site(out_path)

        site.include(str(self.file_path))
        site.render()

        assert (out_path / 'test.html').exists()
        assert (out_path / 'test.html').read_text() == self.test_content

    def test_not_found(self, tmp_path: Path):
        out_path = tmp_path / 'out'
        site = Site(out_path)

        with pytest.raises(FileNotFoundError):
            site.include(str(uuid4()))


class TestIncludeDirectory:

    def setup(self):
        self.file_path = Path('test1/test2/test3/test.html')
        self.test_content = 'This is a test!'
        self.file_path.parent.mkdir(parents=True)
        with self.file_path.open('w') as f:
            f.write(self.test_content)

    def teardown(self):
        shutil.rmtree('test1')

    def test_include(self, tmp_path: Path):
        out_path = tmp_path / 'out'
        site = Site(out_path)

        site.include('test1')
        site.render()

        assert (out_path / 'test1/test2/test3/test.html').exists()
        assert (out_path / 'test1/test2/test3/test.html').read_text() == self.test_content
