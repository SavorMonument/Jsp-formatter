### JSP formatter
    - had a project with tons of unformmated jsp files and couldn't find a decent free jsp formmater
        with minimal dependecies so made this, it is far from perfect but it works decently well

#### Settings for neoformat

```
    let g:neoformat_jsp_custom = {
                \ 'exe': '[path-to-script]',
                \ 'stdin': 0,
                \ 'valid_exit_codes': [0],
                \ }

    let g:neoformat_enabled_jsp = ['custom']
```

        
