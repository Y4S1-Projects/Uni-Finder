// ─────────────────────────────────────────────
// Shared / OL constants
// ─────────────────────────────────────────────
export const STREAMS = ["Science", "Commerce", "Arts", "Technology"];

export const SRI_LANKA_AL_SUBJECTS = [
	// Science
	"Combined Mathematics",
	"Physics",
	"Chemistry",
	"Biology",
	"Agriculture",
	"Information & Communication Technology",

	// Technology
	"Engineering Technology",
	"Bio Systems Technology",
	"Science for Technology",

	// Commerce
	"Accounting",
	"Business Studies",
	"Economics",
	"Business Statistics",

	// Arts / Languages / Social Sciences
	"Sinhala",
	"Tamil",
	"English",
	"Buddhism",
	"Hinduism",
	"Christianity",
	"Islam",
	"History",
	"Geography",
	"Political Science",
	"Logic and Scientific Method",
	"Communication and Media Studies",
	"Home Economics",
	"Dancing",
	"Music",
	"Art",
	"Drama and Theatre",
	"Pali",
	"Sanskrit",

	// Other
	"Greek and Roman Civilization",
	"Arabic",
	"French",
	"German",
	"Japanese",
	"Chinese",
	"Russian",
	"Korean",
	"Higher Mathematics",
	"ICT",
];

export const PHYSICAL_SCIENCE_INTERESTS = [
	"Engineering",
	"Civil Engineering",
	"Mechanical Engineering",
	"Electrical Engineering",
	"Electronic Engineering",
	"Computer Engineering",
	"Software Engineering",
	"Computer Science",
	"Artificial Intelligence",
	"Data Science",
	"Robotics",
	"Mechatronics",
	"Telecommunications",
	"Renewable Energy",
	"Aerospace Engineering",
	"Architecture",
	"Quantity Surveying",
	"Mathematics",
	"Applied Mathematics",
	"Statistics",
	"Physics",
	"Chemistry",
	"Materials Science",
	"Industrial Engineering",
];

export const SRI_LANKA_DISTRICTS = [
	"Colombo",
	"Gampaha",
	"Kalutara",
	"Kandy",
	"Matale",
	"Nuwara Eliya",
	"Galle",
	"Matara",
	"Hambantota",
	"Jaffna",
	"Kilinochchi",
	"Mannar",
	"Vavuniya",
	"Mullaitivu",
	"Batticaloa",
	"Ampara",
	"Trincomalee",
	"Kurunegala",
	"Puttalam",
	"Anuradhapura",
	"Polonnaruwa",
	"Badulla",
	"Monaragala",
	"Ratnapura",
	"Kegalle",
];

// ─────────────────────────────────────────────
// A/L Wizard — stream definitions
// icon: key used to look up StreamIcons component
// accentFrom / accentTo: Tailwind classes for blue-family palette per stream
// ─────────────────────────────────────────────
export const AL_STREAMS = [
	{
		id: "physical-science",
		name: "Physical Science",
		backendName: "Physical Science",
		icon: "atom",
		accentFrom: "from-blue-500",
		accentTo: "to-cyan-500",
		tagline: "Mathematics, Physics & beyond",
		availableSubjects: [
			"Combined Mathematics",
			"Physics",
			"Chemistry",
			"Information & Communication Technology",
			"Higher Mathematics",
		],
	},
	{
		id: "biological-science",
		name: "Biological Science",
		backendName: "Biological Science",
		icon: "biology",
		accentFrom: "from-indigo-500",
		accentTo: "to-blue-400",
		tagline: "Life sciences & health pathways",
		availableSubjects: [
			"Biology",
			"Chemistry",
			"Physics",
			"Agricultural Science",
			"Information & Communication Technology",
		],
	},
	{
		id: "commerce",
		name: "Commerce",
		backendName: "Commerce",
		icon: "commerce",
		accentFrom: "from-blue-600",
		accentTo: "to-indigo-500",
		tagline: "Business, accounting & economics",
		availableSubjects: [
			"Accounting",
			"Business Studies",
			"Economics",
			"Business Statistics",
			"Geography",
			"Political Science",
			"History",
			"Logic & Scientific Method",
			"English",
			"Information & Communication Technology",
			"Agricultural Science",
			"Combined Mathematics",
			"Physics",
			"French",
			"German",
		],
	},
	{
		id: "engineering-technology",
		name: "Engineering Technology",
		backendName: "Engineering Technology",
		icon: "engineering",
		accentFrom: "from-cyan-500",
		accentTo: "to-blue-600",
		tagline: "Applied engineering & technology",
		availableSubjects: [
			"Engineering Technology",
			"Science for Technology",
			"Information & Communication Technology",
			"Economics",
			"Geography",
			"Home Economics",
			"English",
			"Communication & Media Studies",
			"Art",
			"Business Studies",
			"Accounting",
			"Mathematics",
			"Agricultural Science",
		],
	},
	{
		id: "bio-systems-technology",
		name: "Bio-Systems Technology",
		backendName: "Bio-Systems Technology",
		icon: "biosystems",
		accentFrom: "from-sky-500",
		accentTo: "to-blue-500",
		tagline: "Bio-technology & agri-systems",
		availableSubjects: [
			"Bio-Systems Technology",
			"Science for Technology",
			"Information & Communication Technology",
			"Economics",
			"Geography",
			"Home Economics",
			"English",
			"Communication & Media Studies",
			"Art",
			"Business Studies",
			"Accounting",
			"Mathematics",
			"Agricultural Science",
		],
	},
	{
		id: "arts",
		name: "Arts",
		backendName: "Arts",
		icon: "arts",
		accentFrom: "from-violet-500",
		accentTo: "to-blue-500",
		tagline: "Humanities, languages & social sciences",
		availableSubjects: [
			"Economics",
			"Geography",
			"History",
			"Accounting",
			"Business Statistics",
			"Political Science",
			"Logic & Scientific Method",
			"Home Economics",
			"Communication & Media Studies",
			"Information & Communication Technology",
			"Agricultural Science",
			"Combined Mathematics",
			"Higher Mathematics",
			"Buddhism",
			"Hinduism",
			"Christianity",
			"Islam",
			"Islamic Civilization",
			"Greek & Roman Civilization",
			"Art",
			"Dance",
			"Music",
			"Drama",
			"Sinhala",
			"Tamil",
			"English",
			"Arabic",
			"Pali",
			"Sanskrit",
			"French",
			"German",
			"Russian",
			"Japanese",
			"Chinese",
			"Hindi",
			"Civil Tech",
			"Mechanical Tech",
			"Electrical/Electronic Tech",
			"Food Tech",
			"Agro Tech",
			"Bio-Resource Tech",
		],
	},
];

// ─────────────────────────────────────────────
// A/L Wizard — subject combination validation rules
// Returns an error string or "" if valid
// ─────────────────────────────────────────────
export function getSubjectRuleError(streamName, subjects) {
	if (!streamName || subjects.length !== 3) return "";

	const set = new Set(subjects);
	const has = (s) => set.has(s);
	const countIn = (pool) => subjects.filter((s) => pool.includes(s)).length;

	if (streamName === "Physical Science") {
		if (!has("Combined Mathematics") || !has("Physics"))
			return "Physical Science requires Combined Mathematics and Physics as compulsory subjects.";
		const optionals = ["Chemistry", "Information & Communication Technology", "Higher Mathematics"];
		if (countIn(optionals) !== 1)
			return "Physical Science requires exactly one optional: Chemistry, ICT, or Higher Mathematics.";
	}

	if (streamName === "Biological Science") {
		if (!has("Biology") || !has("Chemistry"))
			return "Biological Science requires Biology and Chemistry as compulsory subjects.";
		const optionals = ["Physics", "Agricultural Science", "Information & Communication Technology"];
		if (countIn(optionals) !== 1)
			return "Biological Science requires exactly one optional: Physics, Agricultural Science, or ICT.";
	}

	if (streamName === "Commerce") {
		const standard = ["Accounting", "Business Studies", "Economics"];
		if (countIn(standard) < 2) return "Commerce requires at least two of Accounting, Business Studies, and Economics.";
	}

	if (streamName === "Engineering Technology") {
		if (!has("Engineering Technology") || !has("Science for Technology"))
			return "Engineering Technology stream requires Engineering Technology and Science for Technology.";
	}

	if (streamName === "Bio-Systems Technology") {
		if (!has("Bio-Systems Technology") || !has("Science for Technology"))
			return "Bio-Systems Technology stream requires Bio-Systems Technology and Science for Technology.";
	}

	if (streamName === "Arts") {
		const artsTech = [
			"Civil Tech",
			"Mechanical Tech",
			"Electrical/Electronic Tech",
			"Food Tech",
			"Agro Tech",
			"Bio-Resource Tech",
		];
		if (countIn(artsTech) > 1) return "Arts stream allows a maximum of one technological subject.";
	}

	return "";
}
