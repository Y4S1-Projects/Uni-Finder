import React, { useState, useRef, useEffect } from "react";
import { twMerge } from "tailwind-merge";
import { FormLabel, FormHelperText, formStyles } from "./FormUtils";

const Dropdown = ({
	options = [],
	placeholder = "Please select",
	defaultOption = null,
	defaultOptions = [],
	displayKey = "name",
	idKey = "id",
	isSearchable = false,
	disabled = false,
	wrapperClassName = "",
	buttonClassName = "",
	dropdownClassName = "",
	optionClassName = "",
	filterClassName = "",
	outerContainerStyle = "",
	onSelect,
	error,
	label,
	labelStyle,
	labelClassName,
	helpText,
	helpTextStyle,
	errorTextStyle,
	isRequired = false,
	name,
	onBlur,
	onFocus,
	isFilterSearch = false,
	multiple = false,
	prefixIcon = null,
}) => {
	const [isOpen, setIsOpen] = useState(false);
	const [searchTerm, setSearchTerm] = useState("");
	const [selectedOption, setSelectedOption] = useState(defaultOption);
	const [selectedOptions, setSelectedOptions] = useState(defaultOptions || []);
	const [focusedIndex, setFocusedIndex] = useState(-1);
	const [isSearchMode, setIsSearchMode] = useState(false);
	const dropdownRef = useRef(null);
	const buttonRef = useRef(null);
	const hiddenInputRef = useRef(null);
	const optionRefs = useRef([]);
	const listboxId = `${name || "dropdown"}-listbox`;

	useEffect(() => {
		const handleClickOutside = (event) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
				setIsOpen(false);
				setSearchTerm("");
				if (onBlur && name) {
					const value = multiple ? selectedOptions : selectedOption;
					onBlur({ target: { name, value } });
				}
			}
		};

		document.addEventListener("mousedown", handleClickOutside);
		return () => document.removeEventListener("mousedown", handleClickOutside);
	}, [multiple, selectedOption, selectedOptions, name, onBlur]);

	useEffect(() => {
		if (defaultOption !== null && defaultOption !== undefined && !multiple) {
			setSelectedOption(defaultOption);
		}
	}, [defaultOption, multiple]);

	useEffect(() => {
		if (multiple && defaultOptions && defaultOptions.length > 0) {
			setSelectedOptions(defaultOptions);
		}
	}, [defaultOptions, multiple]);

	useEffect(() => {
		if (isOpen) {
			setFocusedIndex(-1);
			if (isSearchable && hiddenInputRef.current) {
				setTimeout(() => {
					hiddenInputRef.current?.focus();
				}, 100);
			}
		} else {
			setIsSearchMode(false);
			setSearchTerm("");
		}
	}, [isOpen, isSearchable]);

	useEffect(() => {
		if (focusedIndex >= 0 && optionRefs.current[focusedIndex]) {
			optionRefs.current[focusedIndex].scrollIntoView({
				block: "nearest",
				behavior: "smooth",
			});
		}
	}, [focusedIndex]);

	const handleKeyDown = (e) => {
		if (!isOpen) {
			if (e.key === "Enter" || e.key === " ") {
				e.preventDefault();
				setIsOpen(true);
			}
			return;
		}

		const filteredOptions = options.filter((option) =>
			getDisplayValue(option).toLowerCase().includes(searchTerm.toLowerCase()),
		);

		switch (e.key) {
			case "ArrowDown":
				e.preventDefault();
				setFocusedIndex((prev) => (prev < filteredOptions.length - 1 ? prev + 1 : prev));
				break;
			case "ArrowUp":
				e.preventDefault();
				setFocusedIndex((prev) => (prev > 0 ? prev - 1 : 0));
				break;
			case "Enter":
				e.preventDefault();
				if (focusedIndex >= 0 && focusedIndex < filteredOptions.length) {
					handleSelect(filteredOptions[focusedIndex]);
				}
				break;
			case "Escape":
				e.preventDefault();
				setIsOpen(false);
				break;
			default:
				if (isSearchable && e.key.length === 1) {
					setIsSearchMode(true);
				}
		}
	};

	const handleHiddenInputChange = (e) => {
		if (isSearchable) {
			setSearchTerm(e.target.value);
			setIsSearchMode(true);
		}
	};

	const handleSelect = (option) => {
		if (multiple) {
			const isSelected = selectedOptions.some((item) => item[idKey] === option[idKey]);

			let newSelectedOptions;
			if (isSelected) {
				newSelectedOptions = selectedOptions.filter((item) => item[idKey] !== option[idKey]);
			} else {
				newSelectedOptions = [...selectedOptions, option];
			}

			setSelectedOptions(newSelectedOptions);
			onSelect && onSelect(newSelectedOptions);

			if (name && onBlur) {
				onBlur({ target: { name, value: newSelectedOptions } });
			}
		} else {
			setSelectedOption(option);
			setIsOpen(false);
			onSelect && onSelect(option);

			if (name && onBlur) {
				onBlur({ target: { name, value: option } });
			}
		}
	};

	const handleRemoveOption = (optionToRemove, e) => {
		e.stopPropagation();
		e.preventDefault();

		const newSelectedOptions = selectedOptions.filter((item) => item[idKey] !== optionToRemove[idKey]);

		setSelectedOptions(newSelectedOptions);
		onSelect && onSelect(newSelectedOptions);

		if (name && onBlur) {
			onBlur({ target: { name, value: newSelectedOptions } });
		}

		setTimeout(() => {
			buttonRef.current?.focus();
		}, 0);
	};

	const handleBlur = (e) => {
		const isRemoveButtonClick = e.relatedTarget?.closest('[role="button"][aria-label*="Remove"]');

		if (isRemoveButtonClick) {
			return;
		}

		setTimeout(() => {
			if (!dropdownRef.current?.contains(document.activeElement)) {
				setIsOpen(false);
				if (onBlur && name) {
					const value = multiple ? selectedOptions : selectedOption;
					onBlur({ target: { name, value } });
				}
			}
		}, 100);
	};

	const handleButtonClick = () => {
		if (!disabled) {
			setIsOpen(!isOpen);
			if (onFocus && !isOpen) {
				onFocus({ target: { name } });
			}
		}
	};

	const handleOptionMouseEnter = (index) => {
		setFocusedIndex(index);
	};

	const getDisplayValue = (option) => {
		if (!option) return "";
		if (displayKey?.includes("+")) {
			return displayKey
				.split("+")
				.map((key) => option[key.trim()])
				.join(" ");
		}
		return option[displayKey] || "";
	};

	const isOptionSelected = (option) => {
		if (!multiple) return selectedOption?.[idKey] === option[idKey];
		return selectedOptions.some((item) => item[idKey] === option[idKey]);
	};

	const filteredOptions = options.filter((option) =>
		getDisplayValue(option).toLowerCase().includes(searchTerm.toLowerCase()),
	);

	const getBorderClasses = () => {
		if (isOpen) return "border border-purple-400";
		return "border-0";
	};

	const baseClasses = twMerge(formStyles.dropDown, getBorderClasses());

	const renderSelectedTags = () => {
		if (!multiple || selectedOptions.length === 0) {
			return <span className='text-gray-400 truncate'>{placeholder}</span>;
		}

		return (
			<div className='flex flex-wrap gap-1 overflow-y-auto sm:gap-2 max-h-20'>
				{selectedOptions.map((option) => (
					<div
						key={option[idKey]}
						className='flex items-center gap-1 bg-[#383838] text-white px-[4px] sm:px-2 py-1 rounded-md '>
						<span
							className='truncate max-w-24 sm:max-w-32 md:max-w-40 text-[8px] sm:text-[10px] md:text-[14px]'
							title={getDisplayValue(option)}>
							{getDisplayValue(option)}
						</span>
						<span
							onClick={(e) => handleRemoveOption(option, e)}
							className='flex items-center justify-center flex-shrink-0 w-3 h-3 transition-colors rounded-full cursor-pointer sm:w-4 sm:h-4 hover:bg-gray-600'
							role='button'
							tabIndex={0}
							onKeyDown={(e) => {
								if (e.key === "Enter" || e.key === " ") {
									handleRemoveOption(option, e);
								}
							}}
							aria-label={`Remove ${getDisplayValue(option)}`}>
							<svg
								width='10'
								height='10'
								viewBox='0 0 12 12'
								fill='none'
								xmlns='http://www.w3.org/2000/svg'
								className='sm:w-3 sm:h-3'>
								<path
									d='M9 3L3 9M3 3L9 9'
									stroke='currentColor'
									strokeWidth='1.5'
									strokeLinecap='round'
									strokeLinejoin='round'
								/>
							</svg>
						</span>
					</div>
				))}
			</div>
		);
	};

	const getButtonDisplayText = () => {
		if (multiple) {
			return null;
		}

		if (isSearchable && isSearchMode && searchTerm) {
			return searchTerm;
		}

		if (selectedOption) {
			return getDisplayValue(selectedOption);
		}

		return placeholder;
	};

	return (
		<div className={twMerge("flex flex-col w-full", outerContainerStyle)}>
			<FormLabel
				label={label}
				isRequired={isRequired}
				className={labelClassName || labelStyle}
				helpText={helpText}
				prefixIcon={prefixIcon}
			/>

			{helpText && (
				<div className='flex items-center h-[15px] sm:h-5 mb-1 sm:mb-2'>
					<span className={twMerge(formStyles.helpText, helpTextStyle)}>{helpText}</span>
				</div>
			)}

			<div ref={dropdownRef} className={`relative ${wrapperClassName}`}>
				{isSearchable && (
					<input
						ref={hiddenInputRef}
						type='text'
						value={searchTerm}
						onChange={handleHiddenInputChange}
						onKeyDown={handleKeyDown}
						onBlur={handleBlur}
						className='absolute opacity-0 pointer-events-none -z-10'
						autoComplete='off'
						inputMode='text'
						aria-hidden='true'
						tabIndex={-1}
					/>
				)}

				<button
					ref={buttonRef}
					type='button'
					onClick={handleButtonClick}
					onKeyDown={handleKeyDown}
					onBlur={handleBlur}
					className={twMerge(baseClasses, "h-9 sm:h-[44px]", buttonClassName)}
					aria-expanded={isOpen ? "true" : "false"}
					aria-controls={listboxId}
					aria-haspopup='listbox'
					role='combobox'>
					{multiple ?
						<div className='flex-1 text-left'>{renderSelectedTags()}</div>
					:	<span
							className={twMerge(
								"block truncate text-[10px] sm:text-base text-left",
								selectedOption ? "text-gray-700 font-medium" : "text-gray-400",
								isSearchMode && searchTerm ? "text-gray-700" : "",
							)}
							title={getButtonDisplayText()}>
							{getButtonDisplayText()}
							{isSearchable && isSearchMode && isOpen && <span className='animate-pulse'>|</span>}
						</span>
					}

					<div className='flex items-center flex-shrink-0 ml-2'>
						{isOpen ?
							<svg
								width='21'
								height='10'
								viewBox='0 0 25 12'
								fill='none'
								xmlns='http://www.w3.org/2000/svg'
								className='sm:w-6 sm:h-3'>
								<g clipPath='url(#clip0_56_386)'>
									<path
										fillRule='evenodd'
										clipRule='evenodd'
										d='M11.289 1.843L5.63198 7.5L7.04598 8.914L11.996 3.964L16.946 8.914L18.36 7.5L12.703 1.843C12.5155 1.65553 12.2611 1.55022 11.996 1.55022C11.7308 1.55022 11.4765 1.65553 11.289 1.843Z'
										fill='#686868'
									/>
								</g>
								<defs>
									<clipPath id='clip0_56_386'>
										<rect width='12' height='24' fill='white' transform='matrix(0 -1 -1 0 24 12)' />
									</clipPath>
								</defs>
							</svg>
						:	<svg
								width='21'
								height='10'
								viewBox='0 0 25 12'
								fill='none'
								xmlns='http://www.w3.org/2000/svg'
								className='sm:w-6 sm:h-3'>
								<g clipPath='url(#clip0_1337_5289)'>
									<path
										fillRule='evenodd'
										clipRule='evenodd'
										d='M11.7889 10.1569L6.13186 4.49994L7.54586 3.08594L12.4959 8.03594L17.4459 3.08594L18.8599 4.49994L13.2029 10.1569C13.0153 10.3444 12.761 10.4497 12.4959 10.4497C12.2307 10.4497 11.9764 10.3444 11.7889 10.1569Z'
										fill='#686868'
									/>
								</g>
								<defs>
									<clipPath id='clip0_1337_5289'>
										<rect width='12' height='24' fill='white' transform='matrix(0 1 -1 0 24.5 0)' />
									</clipPath>
								</defs>
							</svg>
						}
					</div>
				</button>

				{isOpen && (
					<div
						className={twMerge("absolute mt-1 w-full z-10 bg-white rounded-md shadow-lg", dropdownClassName)}
						id={listboxId}
						role='listbox'>
						<div className={twMerge("max-h-48 sm:max-h-60 overflow-y-auto", filterClassName)}>
							{filteredOptions.map((option, index) => (
								<div
									key={option[idKey]}
									ref={(el) => (optionRefs.current[index] = el)}
									onClick={(e) => {
										e.preventDefault();
										e.stopPropagation();
										handleSelect(option);
									}}
									onMouseDown={(e) => {
										e.preventDefault();
									}}
									onMouseEnter={() => handleOptionMouseEnter(index)}
									className={twMerge(
										"py-2 sm:py-3 px-3 sm:px-4 cursor-pointer text-sm sm:text-base",
										formStyles.dropDownOptions,
										optionClassName,
										isOptionSelected(option) ? "bg-purple-100 text-purple-700 font-semibold" : "",
										focusedIndex === index && !isOptionSelected(option) ? "bg-purple-50" : "",
									)}
									title={getDisplayValue(option)}
									role='option'
									aria-selected={isOptionSelected(option)}>
									{getDisplayValue(option)}
								</div>
							))}
							{filteredOptions.length === 0 && (
								<div className='px-3 py-2 text-sm text-center text-gray-500 sm:px-4 sm:py-3 sm:text-base'>
									{searchTerm ? "No results found" : "No options available"}
								</div>
							)}
						</div>
					</div>
				)}

				<FormHelperText error={!isFilterSearch ? error : null} errorClassName={errorTextStyle} />
			</div>
		</div>
	);
};

export default Dropdown;
