// Filename - App.js
 
import axios from "axios";
 
import React, { Component } from "react";
 
class App extends Component {
    state = {
        // Initially, no file is selected
        selectedFile: null,
        fileDescription: "", // Добавляем новое поле для хранения описания файла
    };
 
    // On file select (from the pop up)
    onFileChange = (event) => {
        // Update the state
        this.setState({
            selectedFile: event.target.files[0],
        });
    };

    onDescriptionChange = (event) => {
      this.setState({
          fileDescription: event.target.value,
      });
    };
 
    // On file upload (click the upload button)
    onFileUpload = () => {
      if (this.state.selectedFile) {
        // Create an object of formData
        const formData = new FormData();
 
        // Update the formData object
        formData.append(
            "myFile",
            this.state.selectedFile,
            this.state.selectedFile.name
        );
          
        // Details of the uploaded file
        console.log(this.state.selectedFile);

        formData.append("filedescription", this.state.fileDescription); // Используем описание из состояния
 
        // Request made to the backend api
        // Send formData object
        // axios.post("api/uploadfile", formData);
        console.log(this.state.fileDescription);
        } else {
            alert("Пожалуйста, выберите файл для загрузки");
        }
    };
 
    // File content to be displayed after
    // file upload is complete
    fileData = () => {
        if (this.state.selectedFile) {
            return (
                <div>
                    <h2>Информация о файле:</h2>
                    <p>
                        Имя файла:{" "}
                        {this.state.selectedFile.name}
                    </p>
 
                    <p>
                        Тип файла:{" "}
                        {this.state.selectedFile.type}
                    </p>
 
                    <p>
                        Последние изменения:{" "}
                        {this.state.selectedFile.lastModifiedDate.toDateString()}
                    </p>
                    <input placeholder="Описание файла" value={this.state.fileDescription} onChange={this.onDescriptionChange} />
                </div>
            );
        } else {
            return (
                <div>
                    <br />
                    <h4>
                        Нет выбраных файлов
                    </h4>
                </div>
            );
        }
    };
 
    render() {
        return (
            <div>
                <h1>Файл помойка</h1>
                <h3>Загрузка файлов с помощью реакт</h3>
                <div>
                    <input
                        type="file"
                        onChange={this.onFileChange}
                    />
                    <button onClick={this.onFileUpload}>
                        Загрузить
                    </button>
                </div> 
                {this.fileData()}
            </div>
        );
    }
}
 
export default App;
