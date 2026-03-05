import React, { useId } from "react";
import { Form } from "react-bootstrap";

export default function DatalistInput({
	label,
	value,
	onChange,
	options,
	placeholder,
	required,
	disabled,
	type = "text",
	error,
	helpText,
	id,
}) {
	const autoId = useId();
	const inputId = id || `datalist-input-${autoId}`;
	const listId = `${inputId}-list`;

	return (
		<Form.Group>
			{label ? <Form.Label className='fw-semibold'>{label}</Form.Label> : null}
			<Form.Control
				id={inputId}
				type={type}
				list={listId}
				value={value}
				onChange={onChange}
				placeholder={placeholder}
				required={required}
				disabled={disabled}
				isInvalid={Boolean(error)}
			/>
			<datalist id={listId}>
				{(options || []).map((opt) => (
					<option key={opt} value={opt} />
				))}
			</datalist>
			{helpText ? <Form.Text className='text-muted'>{helpText}</Form.Text> : null}
			{error ? <Form.Control.Feedback type='invalid'>{error}</Form.Control.Feedback> : null}
		</Form.Group>
	);
}
