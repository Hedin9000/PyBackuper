# PyBackuper
####  Configuration
```json
{
  "RootFolder": "D:/AppsWorkfolder/PyBackuper/",
  "StoreItems": [
    {
      "Name": "PyFile",
      "Path": "D:\\MaximumConfigExample\\main.py",
      "InnerPath": "test/file.py",
      "Zip": false,      
      "Condition": "Always", // Always | IfUpdated
      "Enabled" : false
    },
    {
      "Path": "D:/MinimumConfigExample/MyItem"
    }
  ]
}
```
##### TODO:
1. Encryption
2. Compression level selection
3. Multi-root system 
4. Categories 
5. Logfile
6. Recover mode
7. Rollback if error