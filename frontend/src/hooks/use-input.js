import { useState } from "react";

export function useInput(defaultValue, validationFunction) {
  const [enteredValue, setEnteredValue] = useState(defaultValue);
  const [didEdit, setDidEdit] = useState(false);

  function handleInputChange(event) {
    const { value } = event.target;
    setEnteredValue(value);
    setDidEdit(false);
  }

  function handleInputBlur() {
    setDidEdit(true);
  }

  function setValue(value) {
    setEnteredValue(value);
    setDidEdit(false);
  }

  function reset() {
    setEnteredValue(defaultValue);
    setDidEdit(false);
  }

  const valueIsValid = validationFunction
    ? validationFunction(enteredValue) === ""
    : true;

  return {
    value: enteredValue,
    setValue,
    handleInputChange,
    handleInputBlur,
    hasError: didEdit && !valueIsValid,
    errorMessage: validationFunction ? validationFunction(enteredValue) : "",
    reset,
  };
}
