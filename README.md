# write-me

Something new about your Telegram messages.

### Setup

```sh
$ git clone https://github.com/alena-bartosh/write-me.git && cd write-me/
$ python3 -m venv .env
$ echo 'export PATH=$(pwd)/src:$PATH' >> .env/bin/activate
$ source .env/bin/activate
$ pip install -r requirements.txt
```

### Prepare and Run

1. Export chat history with specific person in HTML format.
2. Resulting dir will contain files like *"messages.html"*. Copy path to this dir.

   (in the virtual environment)

    ```sh
    $ src/main.py -p ABSOLUTE_PATH_TO_DIR
    ```

3. Open *http://localhost:3838/* to see the results.
4. For self research, you can run jupyter notebook.

   ```sh
   $ python3 -m ipykernel install --user --name=.env
   $ jupyter notebook ./ipynb
   ```

### Usage

```
src/main.py --help

usage: main.py [-h] [--log-level] -p

[write-me] Write & analyze your Telegram messages

options:
  -h, --help       show this help message and exit
  --log-level      debug/info/warning/error

required arguments:
  -p , --pathdir   dir with exported messages in .html
```

### Code conduction

* Use [Gitmoji](https://gitmoji.dev/) for commit messages
