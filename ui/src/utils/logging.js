import axios from 'axios';

export async function logEvent(sourcePath, path, action, category, label) {
  // DEBUG
  //    console.log("log event sourcePath=" + sourcePath + " path=" + path + " action=" + action + " category=" + category + " label=" + label);

  axios
    .post(`/api/log`, {
      sourcePath: sourcePath,
      path: path,
      action: action,
      category: category,
      label: label,
    })
    .then(response => {
      //	console.log("/api/log returned status = " + response.status);
    })
    .catch(error => {
      console.log('/api/log failed with status ' + error.response.status);
    });
}
