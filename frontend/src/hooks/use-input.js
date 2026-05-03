import { useCallback, useState } from "react";

export function useInput(defaultValue, validationFunction) {
  const isObjectMode =
    !validationFunction &&
    defaultValue !== null &&
    typeof defaultValue === "object" &&
    !Array.isArray(defaultValue);

  const [values, setValuesState] = useState(isObjectMode ? defaultValue : {});
  const [enteredValue, setEnteredValue] = useState(defaultValue);
  const [didEdit, setDidEdit] = useState(false);

  const handleInputChange = useCallback((event) => {
    const { value } = event.target;
    setEnteredValue(value);
    setDidEdit(false);
  }, []);

  const handleInputBlur = useCallback(() => {
    setDidEdit(true);
  }, []);

  const setValue = useCallback((value) => {
    setEnteredValue(value);
    setDidEdit(false);
  }, []);

  const reset = useCallback(() => {
    setEnteredValue(defaultValue);
    setDidEdit(false);
  }, [defaultValue]);

  const valueIsValid = validationFunction
    ? validationFunction(enteredValue) === ""
    : true;

  const handleChange = useCallback((event) => {
    const { name, value, type, checked } = event?.target || {};
    if (!name) return;
    setValuesState((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  }, []);

  const setValues = useCallback((nextValues) => {
    setValuesState((prev) =>
      typeof nextValues === "function" ? nextValues(prev) : nextValues,
    );
  }, []);

  const resetValues = useCallback(() => {
    setValuesState(defaultValue);
  }, [defaultValue]);

  if (isObjectMode) {
    return {
      values,
      handleChange,
      setValues,
      reset: resetValues,
    };
  }

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
