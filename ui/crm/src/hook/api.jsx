import { message } from "antd";
import axios from "axios";

export async function postRequest(url, body) {
  try {
    let response = await axios.post(
      import.meta.env.VITE_APP_BASE_URL + url,
      body,
      generateRequestHeader()
    );
    return response.data;
  } catch (error) {
    handleErrorCode(error);
    throw error;
  }
}
export async function getRequest(url) {
  try {
    let response = await axios.get(
      import.meta.env.VITE_APP_BASE_URL + url,
      generateRequestHeader()
    );
    return response.data;
  } catch (error) {
    handleErrorCode(error);
    throw error;
  }
}

export async function deleteRequest(url) {
  try {
    let response = await axios.delete(
      import.meta.env.VITE_APP_BASE_URL + url,
      generateRequestHeader()
    );
    return response.data;
  } catch (error) {
    handleErrorCode(error);
    throw error;
  }
}

export async function putRequest(url, body) {
  try {
    let response = await axios.put(
      import.meta.env.VITE_APP_BASE_URL + url,
      body,
      generateRequestHeader()
    );
    return response.data;
  } catch (error) {
    handleErrorCode(error);
    throw error;
  }
}

export function generateRequestHeader() {
  return {
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + localStorage.getItem("accessToken"),
    },
  };
}

export const handleErrorCode = (err) => {
  message.error(''+ err)
};
